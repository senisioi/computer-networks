# Capitolul X10: Load Balancers — Distribuirea traficului între replici

În capitolul anterior (X9) ați rulat frontend, API și PostgreSQL și ați observat cum Kubernetes poate scala orizontal Deployment-uri (mai multe pod-uri care servesc aceeași aplicație). Un singur Service de tip ClusterIP poate ruta automat cererile între aceste pod-uri — dar cum se întâmplă concret distribuția și ce rol au load balancer-ele și health check-urile?

În acest seminar construim o arhitectură minimală, gândită să vă arate practic cum circulă traficul:

- **API FastAPI cu identitate vizibilă** — fiecare pod răspunde cu hostname-ul și IP-ul din cluster, pentru a putea observa clar unde ajunge request-ul tău.
- **3 replici și health checks** — Deployment cu 3 pod-uri, `readinessProbe` și `livenessProbe` pentru a discuta despre disponibilitate (*availability*) și autoscalarea logică.
- **NGINX ca reverse proxy** — un punct de intrare NodePort către API, cu setări care închid conexiunea TCP după fiecare răspuns trimis spre upstream. Astfel, un lanț de comenzi `curl` va evidenția clar cum se face rotația între replici.
- **Sticky sessions** la nivel de Kubernetes Service (`sessionAffinity: ClientIP`), echivalent practic cu „tot traficul de la același IP sursă merge mereu la același pod” — ca să vedem diferența față de distribuirea echilibrată (default).

---

## Cuprins

- [Ce este un Load Balancer?](#ce-este-un-load-balancer)
- [Straturi OSI — L4 vs L7](#straturi-osi-l4-l7)
- [Algoritmi clasici](#algoritmi-clasici)
- [Health Checks](#health-check-uri)
- [Arhitectura laboratorului](#arhitectura-laboratorului)
- [Pasul 0: Pregătirea mediului](#pasul-0-pregătirea-mediului)
- [Pasul 1: Construirea imaginii Docker](#pasul-1-construirea-imaginii-docker)
- [Pasul 2: Deploy în Kubernetes](#pasul-2-deploy-în-kubernetes)
- [Pasul 3: Verificare rapidă](#pasul-3-verificare-rapidă)
- [Pasul 4: Curățarea mediului](#pasul-4-curățarea-mediului)
- [Exerciții practice](#exerciții-practice)

---

## Ce este un Load Balancer?

Un **load balancer** este o componentă de rețea (sau o serie de reguli de rutare) care primește trafic de la clienți și îl împarte între mai multe instanțe ale aceluiași serviciu (servere, pod-uri, mașini virtuale). Motivele principale pentru care le folosim:

1. **Scalabilitate** — creșterea traficului se absoarbe prin adăugarea de replici, nu prin mărirea resurselor unei singure mașini.
2. **Disponibilitate (High Availability)** — dacă o instanță pică, traficul este redirecționat automat către celelalte (pe baza health check-urilor).
3. **Offloading / separarea responsabilităților** — task-uri precum TLS termination, rate limiting sau rutarea pe bază de URL/headere pot fi mutate la „marginea” arhitecturii.

În Kubernetes, un obiect **Service** oferă deja un **virtual IP (ClusterIP)** și echilibrează automat traficul între pod-urile care se potrivesc **selector**-ului. În producție, pe lângă Service, se adaugă adesea un **Ingress** (de obicei NGINX, Traefik, HAProxy) sau un **cloud load balancer** (oferit de AWS/GCP/Azure) în fața clusterului.

---

<a id="straturi-osi-l4-l7"></a>

## Straturi OSI — L4 vs L7

| Aspect | **Stratul 4 (Transport)** | **Stratul 7 (Aplicație)** |
|--------|---------------------------|---------------------------|
| **Criterii de rutare** | Conexiuni TCP/UDP, porturi, IP-uri | HTTP(S), URL, headere, cookie-uri, conținut |
| **Exemple** | echilibrare între IP:port | rutare `/api` vs `/static`, verificarea unui cookie |
| **Avantaje** | foarte rapid, funcționează cu orice protocol | control fin pentru aplicații web și API-uri |
| **Observație** | nu „vede” URL-ul | poate face TLS termination și politici per-rută |

Laboratorul de astăzi folosește **NGINX** pe post de reverse proxy **HTTP (L7)** spre API, în timp ce **kube-proxy** (componenta din spatele unui Service K8s) face forwarding-ul la nivel de rețea către pod-uri (un model mental apropiat de **L4** din perspectiva clusterului).

---

<a id="algoritmi-clasici"></a>

## Algoritmi clasici de distribuție a traficului

1. **Round Robin** — request-urile sunt împărțite pe rând: A, B, C, A, B, C… E simplu și previzibil, dar nu ține cont de cât de încărcat este cu adevărat fiecare server.
2. **Least Connections** — un nou request este trimis către serverul cu **cele mai puține conexiuni active**. Foarte util când unele request-uri durează mult mai mult decât altele.
3. **IP Hash** — se calculează un hash folosind IP-ul clientului (sau o altă cheie). Astfel, același client ajunge mereu la același backend (*sticky sessions*). E vital pentru sistemele cu stare locală (*stateful*), dar poate crea dezechilibre dacă un singur client generează foarte mult trafic.

În Kubernetes, echilibrarea *default* între endpoint-urile unui Service este, teoretic, uniformă între pod-urile READY. Comportamentul exact depinde de cum este implementat kube-proxy în clusterul vostru (**iptables** sau **IPVS**). În acest seminar, variația hostname-urilor din răspunsuri va fi dovada distribuției.

---

## Health check-uri

**Health check**-urile sunt verificări periodice (fie **active** — un request trimis de load balancer, fie **pasive** — monitorizarea erorilor) care răspund la întrebarea: *backend-ul este sănătos și poate primi trafic?*

- **Liveness** — „Procesul trăiește?”. Dacă pică, Kubernetes va reporni containerul.
- **Readiness** — „Poate servi trafic în acest moment?”. Dacă pică, pod-ul este scos din rotația Service-ului până își revine.

Fără o probă de **readiness**, un pod care de abia pornește (și încă își încarcă datele) ar primi trafic și ar da erori. Health check-urile leagă starea reală a aplicației de direcționarea traficului.

În `k8s/api-deployment.yaml`, API-ul nostru expune ruta `GET /health` care este folosită de ambele probe.

---

## Arhitectura laboratorului

```
                    Namespace: laborator-lb

  Browser / curl pe gazdă (localhost :30808, :30809 cu kind-config.yaml)
        │
        │  NodePort :30808
        ▼
  ┌─────────────────────┐        ClusterIP :8000      ┌──────────────────────────┐
  │  nginx-lb-service   │ ───────────────────────────►│  lb-api-backend          │
  │  (NGINX reverse     │   (fără sessionAffinity   │  (3 × pod-uri FastAPI,    │
  │   proxy, 1 replică) │    specific — distribuire   │   round-robin între ei) │
  └─────────────────────┘    echidistantă implicit) └──────────────────────────┘

  Opțional — test direct sticky (Exercițiul 3):
  curl ──► NodePort :30809 (Serviciul `lb-api-student-nodeport`, cu sessionAffinity editabil)
```

**Important:** Dacă trimiteți traficul prin NGINX către Service-ul intern (`lb-api-backend`), IP-ul „clientului” pe care îl vede kube-proxy este **IP-ul podului NGINX**, nu cel al calculatorului vostru. De aceea, pentru a testa corect rutarea *sticky* pe baza IP-ului vostru, vom folosi **`lb-api-student-nodeport`** (care accesează direct pod-urile prin NodePort, ocolind NGINX-ul).

---

## Pasul 0: Pregătirea mediului

Pentru ca aceleași comenzi să funcționeze indiferent dacă folosiți **Linux**, **macOS** sau **Windows** (Docker Desktop), vom crea clusterul folosind un fișier de configurare KinD cu **`extraPortMappings`**. Acesta mapează porturile **30808** și **30809** de pe nodul din cluster direct pe **localhost**-ul vostru.

Fișierul se află în directorul acestui capitol (`kind-config.yaml`).

```bash
cd capitolulX10   # adaptați calea dacă lucrați din alt director

kind create cluster --name k8s-lb --config kind-config.yaml
kubectl cluster-info --context kind-k8s-lb
```

**De ce ne complicăm cu acest config?** Pe Linux nativ, uneori IP-ul returnat de `kubectl get nodes` este direct accesibil. Dar pe macOS/Windows, acel IP aparține mașinii virtuale ascunse a Docker-ului și **nu va răspunde** la comenzi `curl` de pe host. Maparea pe **localhost** elimină complet această problemă.

**(Opțional, doar pentru Linux nativ fără fișier de config):** Puteți crea clusterul normal (`kind create cluster --name k8s-lb`) și înlocuiți `127.0.0.1` din exerciții cu adresa IP a nodului obținută prin:

```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
```

---

## Pasul 1: Construirea imaginii Docker

```bash
cd api
docker build -t lb-demo-api:v1 .
```

Încărcați imaginea în nodul de control KinD:

```bash
kind load docker-image lb-demo-api:v1 --name k8s-lb
```

Verificați că imaginea a ajuns în cluster:

```bash
docker exec -it k8s-lb-control-plane crictl images | grep lb-demo-api
```

---

## Pasul 2: Deploy în Kubernetes

Dacă vă uitați în fișierul `k8s/loadbalancer.yaml`, veți vedea că NGINX-ul este configurat cu `proxy_http_version 1.0` și `proxy_set_header Connection "Close"`.

**De ce am făcut asta?** Dacă am lăsa conexiunea TCP deschisă (*Keep-Alive*, specific HTTP/1.1), kube-proxy ar trimite tot traficul acelei conexiuni către **același** pod API. Forțând NGINX să deschidă o **nouă** conexiune TCP pentru fiecare request, putem vizualiza efectiv cum face Kubernetes load balancing (*round-robin*) cu fiecare `curl`. Altfel, setările *default* ne-ar strica demo-ul.

Aplicați manifestele în această ordine:

```bash
cd k8s

kubectl apply -f 00-namespace.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f loadbalancer.yaml
```

Așteptați ca pod-urile să fie pornite și gata să primească trafic:

```bash
kubectl rollout status deployment/lb-api-deployment -n laborator-lb --timeout=120s
kubectl rollout status deployment/nginx-lb-deployment -n laborator-lb --timeout=120s
kubectl get pods,svc -n laborator-lb
```

*(Așteptat: 3 pod-uri API `Running`, 1 pod NGINX `Running`; servicii `lb-api-backend`, `lb-api-student-nodeport`, `nginx-lb-service`.)*

---

## Pasul 3: Verificare rapidă

Datorită mapării pe localhost, serviciile NodePort răspund direct:
Daca rulati de mai multe ori curl ar trebui sa obtineti raspunsuri de la replici diferite. 

```bash
echo "Prin NGINX (load balancer / reverse proxy): http://127.0.0.1:30808/"
curl -s "http://127.0.0.1:30808/" | python3 -m json.tool

echo "Direct pe backend (NodePort): http://127.0.0.1:30809/"
curl -s "http://127.0.0.1:30809/" | python3 -m json.tool
```

Exemplu de raspuns:
curl -s "http://127.0.0.1:30808/" | python3 -m json.tool

{
    "message": "Salut de la API-ul de laborator (load balancing). Fiecare replica raspunde cu hostname-ul sau unic.",
    "hostname": "lb-api-deployment-695f689c88-hlf4b",
    "pod_ip": "10.244.0.7",
    "kubernetes": true
}
(base) claudiucreanga@C16706 k8s % curl -s "http://127.0.0.1:30808/" | python3 -m json.tool

{
    "message": "Salut de la API-ul de laborator (load balancing). Fiecare replica raspunde cu hostname-ul sau unic.",
    "hostname": "lb-api-deployment-695f689c88-fmzk4",
    "pod_ip": "10.244.0.5",
    "kubernetes": true
}

**În caz că nu vă merg comenzile de mai sus pe WSL (Docker Desktop)**, uneori NodePort pe `localhost` (`30808`, `30809`) dă reset sau nu răspunde. În **două terminale**, lăsați fiecare `port-forward` pornit, apoi rulați `curl`-urile echivalente:

Înlocuire pentru **`30808`** (prin NGINX):

```bash
kubectl port-forward -n laborator-lb svc/nginx-lb-service 18080:8080
# în alt terminal:
curl -s "http://127.0.0.1:18080/" | python3 -m json.tool
```

Înlocuire pentru **`30809`** (direct pe backend; serviciul are **port cluster 8000**, nu `8080`):

```bash
kubectl port-forward -n laborator-lb svc/lb-api-student-nodeport 18081:8000
# în alt terminal:
curl -s "http://127.0.0.1:18081/" | python3 -m json.tool
```

---

## Exerciții (nu exista tema, nu trebuie uploadate nicaieri).

### Exercițiul 1: Load Balancing prin NGINX

**Scop:** Observați cum 10 request-uri consecutive sunt servite de pod-uri diferite (hostname-ul returnat în JSON se schimbă).

Rulați acest script în terminal:

```bash
for i in $(seq 1 10); do
  echo -n "Cerere $i → "
  curl -s "http://127.0.0.1:30808/" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('hostname','?'))"
done
```

*(**WSL**, cu `port-forward` de la Pasul 3 pe `nginx-lb-service`: lăsați `kubectl port-forward ... 18080:8080` pornit și folosiți același script, înlocuind `30808` cu **`18080` în URL-ul `curl`**: `http://127.0.0.1:18080/`.) La toate exercitiile trebuie sa schimbati portul pe WSL*

**Cerință:** Ganditi-va de ce, uneori, același hostname poate apărea de două ori la rând (*Hint:* gândiți-vă la diferența dintre *round-robin* strict și *random* uniform din iptables). Puteti citi despre asta suplimentar.

---

### Exercițiul 2: Simularea unui fail și Self-Healing

**Scop:** „Omorâți” intenționat un pod API și vedeți cum ReplicaSet-ul îl recreează imediat, în timp ce restul traficului funcționează normal.

Luați lista de pod-uri și copiați numele unuia dintre ele:

```bash
kubectl get pods -n laborator-lb -l app=lb-api -o wide
```

Ștergeți unul dintre pod-uri (înlocuiți `<nume-pod>` cu numele copiat):

```bash
kubectl delete pod <nume-pod> -n laborator-lb
```

Urmăriți cum Kubernetes îl recreează live:

```bash
kubectl get pods -n laborator-lb -l app=lb-api -w
```

*(Ieșiți din watch apăsând Ctrl+C.)*

Rulați imediat bucla `curl` de la Exercițiul 1.

**Cerință:** Ganditi-va ce rol a avut `readinessProbe` în protejarea request-urilor trimise prin `curl` în timp ce noul container se inițializa?

---

### Exercițiul 3: Sticky Sessions pe NodePort (`sessionAffinity`)

**Context:** Dacă vrem ca traficul de la un anumit user să ajungă mereu la același server, folosim afinitatea pe IP (*sticky sessions*). În K8s, pentru a lipi traficul în funcție de IP-ul sursă direct pe obiectul Service, folosim `sessionAffinity: ClientIP`.

**Pași:**

1. Deschideți fișierul `k8s/api-deployment.yaml`. Găsiți definiția Service-ului numit `lb-api-student-nodeport` și adăugați secțiunea de `sessionAffinity` astfel încât să arate așa:

```yaml
spec:
  type: NodePort
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
  selector:
    app: lb-api
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30809
```

2. Aplicați modificarea:

```bash
kubectl apply -f k8s/api-deployment.yaml
```

3. Rulați 10 request-uri direct pe NodePort-ul student (**30809**), adică pe Service-ul unde ați adăugat afinitatea (ocolim NGINX-ul):

```bash
for i in $(seq 1 10); do
  echo -n "Direct $i → "
  curl -s "http://127.0.0.1:30809/" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('hostname','?'))"
done
```

*(**WSL** cu workaround de la Pasul 3: lăsați pornit `kubectl port-forward -n laborator-lb svc/lb-api-student-nodeport 18081:8000` și în buclă folosiți **`http://127.0.0.1:18081/`** în loc de `:30809`.)*

**Ce ar trebui să se întâmple?** Acum ar trebui să vedeți mereu același hostname returnat pentru toate cele 10 request-uri, deoarece IP-ul vostru a fost „lipit” de o anumită replică. Puteți dezactiva setarea ștergând liniile de `sessionAffinity` și reaplicând manifestul ca să vedeți diferența.



# Capitolul X8: Kubernetes — Configurare, Sănătate și Multi-Servicii

În capitolul anterior (X7) am învățat fundamentele: cum să deployăm o singură aplicație pe un cluster KinD, cum să o scalăm și cum Kubernetes o auto-vindecă. Aplicațiile reale nu sunt niciodată un singur container — ele sunt compuse din **mai multe servicii** care colaborează.

În acest capitol vom construi o arhitectură mai realistă: o aplicație Flask care numără vizitele folosind **Redis** ca bază de date partajată. Aceasta ne permite să introducem concepte esențiale de producție:

- **Namespaces** — izolarea resurselor în același cluster
- **ClusterIP vs NodePort** — tipuri de Service și când se folosesc
- **DNS intern Kubernetes** — cum se găsesc serviciile între ele
- **ConfigMaps** — externalizarea configurației din codul aplicației
- **Secrets** — gestionarea datelor sensibile
- **Liveness & Readiness Probes** — cum Kubernetes știe că o aplicație este sănătoasă
- **Resource Requests & Limits** — alocarea responsabilă a resurselor CPU/memorie
- **`kubectl exec`** — acces interactiv în interiorul unui container care rulează

## Cuprins

- [Arhitectura aplicației](#arhitectura-aplicației)
- [Concepte Noi](#concepte-noi)
- [Pasul 0: Pregătirea mediului](#pasul-0-pregătirea-mediului)
- [Pasul 1: Construirea imaginii Flask+Redis](#pasul-1-construirea-imaginii-flaskrediis)
- [Pasul 2: Namespace — izolarea mediului](#pasul-2-namespace--izolarea-mediului)
- [Pasul 3: ConfigMap și Secret — separarea configurației](#pasul-3-configmap-și-secret--separarea-configurației)
- [Pasul 4: Deployarea Redis (ClusterIP)](#pasul-4-deployarea-redis-clusterip)
- [Pasul 5: Deployarea Flask cu Probe-uri și Resource Limits](#pasul-5-deployarea-flask-cu-probe-uri-și-resource-limits)
- [Pasul 6: Testarea aplicației și DNS intern](#pasul-6-testarea-aplicației-și-dns-intern)
- [Pasul 7: Simularea defecțiunii — Readiness Probe în acțiune](#pasul-7-simularea-defecțiunii--readiness-probe-în-acțiune)
- [Pasul 8: Explorarea cu OpenLens](#pasul-8-explorarea-cu-openlens)
- [Pasul 9: Curățarea mediului](#pasul-9-curățarea-mediului)
- [Exerciții Practice](#exerciții-practice)
  - [Exercițiul 5: IP-urile pod-urilor — subnetting, comunicare directă și de ce există Service-urile](#exercițiul-5-ip-urile-pod-urilor--subnetting-comunicare-directă-și-de-ce-există-service-urile)
  - [Exercițiul 6: Network Policies — firewall la nivelul pod-urilor](#exercițiul-6-network-policies--firewall-la-nivelul-pod-urilor)

---

## Arhitectura aplicației

```
┌──────────────────────────────────────────────────────────────────┐
│                      Namespace: seminar                          │
│                                                                  │
│   ┌─────────────────────────┐             ┌──────────────────┐  │
│   │    flask-deployment     │  ClusterIP  │ redis-deployment │  │
│   │       (3 replici)       │────────────>│   (1 replică)    │  │
│   │                         │ redis-svc   │                  │  │
│   │  [Pod 1] [Pod 2] [Pod 3]│  :6379      │     [Pod Redis]  │  │
│   └───────────┬─────────────┘             └──────────────────┘  │
│               │ flask-service                                    │
│               │ (NodePort: 30501)                                │
└───────────────┼──────────────────────────────────────────────────┘
                │
           Browser / curl
```

**Observații cheie din diagramă:**
- Cele 3 replici Flask partajează **același Redis** — de aceea contorul crește indiferent de ce replică servește cererea
- `redis-service` este de tip **ClusterIP** (nu are port pe host) — Redis nu este expus în afara clusterului
- `flask-service` este de tip **NodePort** — Flask este accesibil din browser pe portul `30501`

---

## Concepte Noi

| Concept | Ce face | Comanda rapidă |
|---|---|---|
| **Namespace** | Spațiu de nume izolat în cluster. Ca un "folder" pentru obiectele K8s. | `kubectl get pods -n seminar` |
| **ClusterIP** | Service accesibil doar din interiorul clusterului. Implicit. | Definit în YAML: `type: ClusterIP` |
| **DNS intern** | Kubernetes oferă DNS automat: `<service>.<namespace>.svc.cluster.local` | `curl redis-service:6379` (din pod) |
| **ConfigMap** | Stochează configurație non-sensibilă (chei/valori). | `kubectl get configmap -n seminar` |
| **Secret** | Stochează date sensibile codificate în base64. | `kubectl get secret -n seminar` |
| **Liveness Probe** | Dacă eșuează, containerul este **repornit**. | Definit în spec.containers[].livenessProbe |
| **Readiness Probe** | Dacă eșuează, pod-ul este **scos din Service** (nu mai primește trafic). | Definit în spec.containers[].readinessProbe |
| **Resources** | `requests` = garantat, `limits` = maxim permis. | `kubectl top pods -n seminar` |
| **`kubectl exec`** | Rulează o comandă sau deschide un shell într-un container activ. | `kubectl exec -it <pod> -n seminar -- bash` |

---

## Pasul 0: Pregătirea mediului

<a name="pasul-0"></a>

Asigurați-vă că aveți un cluster KinD funcțional. Puteți reutiliza clusterul din X7 sau crea unul nou:

```bash
# Verificați dacă clusterul din X7 mai există
kind get clusters

#stergem clusterul vechi 
kind delete cluster --name k8s-flask

# Cream unul nou
kind create cluster --name k8s-flask
```

Verificați că `kubectl` comunică cu clusterul:
```bash
kubectl cluster-info --context kind-k8s-flask
```

---

## Pasul 1: Construirea imaginii Flask+Redis

<a name="pasul-1"></a>

Analizați `flask-redis/app.py`. Față de capitolul X7, această versiune:
- Se conectează la **Redis** (adresa e citită din variabila de mediu `REDIS_HOST`)
- Expune două endpointuri de health: `/health/live` și `/health/ready`
- Endpointul `/health/ready` face un `r.ping()` real către Redis — dacă Redis nu răspunde, returnează `503 Service Unavailable`


## Exercitiu 1:

Instalati in dockerfile pachetul curl. 


Construiți imaginea:
```bash
cd flask-redis
docker build -t flask-redis-app:v1 .
```

Încărcați imaginea în KinD (doar imaginea custom — Redis este oficială și va fi descărcată automat):
```bash
kind load docker-image flask-redis-app:v1 --name k8s-flask
```



> **De reținut:** Imaginea `redis:7-alpine` din `03-redis.yaml` are `imagePullPolicy` implicit (`IfNotPresent` pentru imagini cu tag specific), deci KinD o va descărca de pe Docker Hub la prima pornire. Numai imaginile voastre custom trebuie încărcate manual cu `kind load`.

---

## Pasul 2: Namespace — izolarea mediului

<a name="pasul-2"></a>

Un **Namespace** vă permite să separați resursele în cadrul aceluiași cluster. Este util pentru a izola medii (ex: `staging`, `production`) sau echipe diferite fără a crea clustere separate.

Aplicați `00-namespace.yaml`:
```bash
cd ../k8s
kubectl apply -f 00-namespace.yaml
```

Verificați:
```bash
kubectl get namespaces
```
*(Veți vedea `seminar` alături de namespace-urile implicite: `default`, `kube-system`, `kube-public`.)*

De acum înainte, **toate comenzile vor necesita flag-ul `-n seminar`** sau `--namespace seminar` pentru a interacționa cu resursele din namespace-ul nostru. Aceasta este o diferență importantă față de X7 unde foloseam namespace-ul `default`.

---

## Pasul 3: ConfigMap și Secret — separarea configurației

<a name="pasul-3"></a>

### ConfigMap

Deschideți `01-configmap.yaml`. Stochează adresa Redis (`REDIS_HOST`), portul și titlul aplicației. Separând configurația de cod, putem schimba comportamentul aplicației fără a reconstrui imaginea Docker.

```bash
kubectl apply -f 01-configmap.yaml
kubectl get configmap flask-config -n seminar
kubectl describe configmap flask-config -n seminar
```

### Secret

Deschideți `02-secret.yaml`. Valorile dintr-un Secret sunt **codificate în base64** (nu criptate!). Puteți verifica:

```bash
kubectl apply -f 02-secret.yaml

# Vizualizați secretul (valorile sunt base64)
kubectl get secret flask-secret -n seminar -o yaml

# Decodificați valoarea manual pentru a vedea parola reală
kubectl get secret flask-secret -n seminar \
  -o jsonpath='{.data.REDIS_PASSWORD}' | base64 --decode
```

> **Discuție:** Base64 **nu este criptare** — oricine are acces la cluster poate decoda valorile. Secretele Kubernetes sunt mai degrabă o convenție de separare a configurației decât o protecție reală. Soluții pentru criptare adevărată includ: [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets), [HashiCorp Vault](https://www.vaultproject.io/), sau **Encryption at Rest** activat în `kube-apiserver`.

---

## Pasul 4: Deployarea Redis (ClusterIP)

<a name="pasul-4"></a>

Analizați `03-redis.yaml`. Conține:
1. Un **Deployment** cu o singură replică Redis (Redis clasic nu se scalează orizontal fără configurare specială — de aceea `replicas: 1`)
2. Un **Service de tip ClusterIP** — accesibil **doar din interiorul clusterului**, nu de pe mașina locală

```bash
kubectl apply -f 03-redis.yaml
kubectl get pods -n seminar
kubectl get services -n seminar
```

Observați că `redis-service` are `TYPE: ClusterIP` și `EXTERNAL-IP: <none>` — confirmare că nu este expus exterior.

Verificați că Redis rulează:
```bash
kubectl logs deployment/redis-deployment -n seminar
```

---

## Pasul 5: Deployarea Flask cu Probe-uri și Resource Limits

<a name="pasul-5"></a>

Analizați cu atenție `04-flask.yaml` înainte de a-l aplica. Conține mai multe concepte noi simultan:

**`envFrom: configMapRef`** — injectează **toate** perechile cheie/valoare din ConfigMap ca variabile de mediu în container:
```yaml
envFrom:
- configMapRef:
    name: flask-config  # → REDIS_HOST, REDIS_PORT, APP_TITLE devin env vars
```

**`env.valueFrom.secretKeyRef`** — injectează o **cheie specifică** dintr-un Secret:
```yaml
- name: REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: flask-secret
      key: REDIS_PASSWORD
```

**Resource Requests & Limits:**
```yaml
resources:
  requests:
    cpu: "50m"      # Kubernetes garantează minim 50 milicores acestui container
    memory: "64Mi"
  limits:
    cpu: "250m"     # Containerul nu poate folosi mai mult de 250 milicores
    memory: "128Mi" # Dacă depășește, containerul este omorât (OOMKilled)
```

**Liveness vs Readiness Probe** — diferența esențială:
- **Liveness** → eșec = **container repornit** (procesul s-a blocat, nu mai răspunde deloc)
- **Readiness** → eșec = **pod scos din Service** (nu mai primește cereri), dar **nu este repornit**

Aplicați:
```bash
kubectl apply -f 04-flask.yaml
```

Urmăriți pod-urile pornind și trecând prin probe-uri:
```bash
kubectl get pods -n seminar -w
```

*(Inițial pod-urile vor fi în `Running` dar poate `0/1 READY` câteva secunde până readiness probe-ul trece. Așteptați până sunt `1/1 READY`.)*

---

## Pasul 6: Testarea aplicației și DNS intern

<a name="pasul-6"></a>

### Accesarea din browser

Obțineți IP-ul nodului KinD:
```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "Accesați: http://$NODE_IP:30501"
```

Sau folosiți port-forward pentru acces rapid:
```bash
kubectl port-forward service/flask-service 5000:5000 -n seminar
# Deschideți http://localhost:5000
```

Reîmprospătați pagina de mai multe ori. Observați:
- **Contorul crește continuu** — Redis este partajat între toate replicile Flask
- **Numele pod-ului se schimbă** — Service-ul distribuie cererile (load balancing) in anumite cazuri, depinde de OS si cum e facut port forwarding. Mai simplu e sa intram in container
```bash
 kubectl run curl-test --image=curlimages/curl -it --rm -n seminar --restart=Never -- sh
```
si sa rulam:
```bash
 for i in $(seq 1 10); do curl -s http://flask-service:5000/ | grep -o 'flask-deployment[^<]*'; sleep 0.5; done
```

### Explorarea DNS intern cu `kubectl exec`

`kubectl exec` vă permite să rulați comenzi direct în interiorul unui container care rulează — echivalentul lui `docker exec` dar pentru Kubernetes.

```bash
# Intrați într-un shell interactiv în primul pod Flask
kubectl exec -it deployment/flask-deployment -n seminar -- bash

# Din interiorul containerului, testați rezoluția DNS internă Kubernetes:
# Forma scurtă (funcționează din același namespace)
curl http://redis-service:6379

# Forma completă (funcționează din orice namespace)
curl http://redis-service.seminar.svc.cluster.local:6379

# Verificați variabilele de mediu injectate din ConfigMap și Secret
env | grep -E "REDIS|APP_TITLE"

# Ieșiți din container
exit
```

> **Cum funcționează DNS-ul intern?** Kubernetes rulează un server DNS intern (`CoreDNS`) în namespace-ul `kube-system`. Când creați un Service numit `redis-service` în namespace-ul `seminar`, CoreDNS înregistrează automat numele `redis-service.seminar.svc.cluster.local`. Orice Pod din cluster poate rezolva acest nume fără nicio configurare suplimentară.

---

## Pasul 7: Readiness Probe în acțiune

<a name="pasul-7"></a>

Vom demonstra diferența practică dintre Liveness și Readiness Probe simulând o defecțiune a Redis.

**Pasul 1:** Scalați Redis la 0 replici (îl "oprim"):
```bash
kubectl scale deployment/redis-deployment --replicas=0 -n seminar
```

**Pasul 2:** Urmăriți starea pod-urilor Flask în timp real:
```bash
kubectl get pods -n seminar -w
```

În câteva secunde (după 2 eșecuri ale readiness probe-ului, conform `failureThreshold: 2`), veți observa că pod-urile Flask trec de la `1/1 READY` la `0/1 READY`. Ele **continuă să ruleze** (nu sunt repornite), dar **nu mai primesc trafic** de la Service.

**Pasul 3:** Verificați că Service-ul nu mai rutează trafic:
```bash
# Dacă aveți port-forward activ, accesați http://localhost:5000 — va da timeout
# Puteți verifica endpoint-urile Service-ului (lista de pod-uri care primesc trafic):
kubectl get endpoints flask-service -n seminar
# Când Redis e oprit: ENDPOINTS va fi <none>
```

**Pasul 4:** Reporniți Redis și observați recuperarea automată:
```bash
kubectl scale deployment/redis-deployment --replicas=1 -n seminar
kubectl get pods -n seminar -w
# Pod-urile Flask revin la 1/1 READY pe măsură ce readiness probe trece din nou
```

> **Scenariul real:** Într-o aplicație de producție, dacă baza de date are o întrerupere temporară (restart, upgrade), Readiness Probe-ul asigură că niciun trafic nu ajunge la instanțele aplicației care nu pot deservi cereri. Utilizatorii primesc erori de la Load Balancer (ex: `503 Service Unavailable`) în loc de erori confuze din aplicație.

---

## Pasul 8: Explorarea cu OpenLens

<a name="pasul-8"></a>

Deschideți OpenLens și conectați-vă la clusterul `kind-k8s-flask`. Explorați namespace-ul `seminar`:

1. **Workloads → Pods** — selectați namespace-ul `seminar` din dropdown. Observați toate pod-urile (Redis + Flask) și starea lor.
2. Faceți click pe un pod Flask → tab **Logs** pentru a vedea output-ul live.
3. **Config → ConfigMaps** — veți vedea `flask-config` cu valorile sale.
4. **Config → Secrets** — veți vedea `flask-secret`. Click pe el și observați că valorile sunt afișate **decodate** (OpenLens le decodifică automat din base64 — un reminder că Secretele nu sunt cu adevărat secrete fără criptare suplimentară).
5. **Network → Services** — comparați `redis-service` (ClusterIP, fără external IP) cu `flask-service` (NodePort, cu port 30501).
6. **Workloads → Deployments** → click pe `flask-deployment` → **Conditions** — puteți vedea starea Readiness probe-urilor.

---
Doar ca info, nu rulati:

## Pasul 9: Curățarea mediului

<a name="pasul-9"></a>

Puteți șterge doar namespace-ul `seminar` (toate resursele din el vor fi șterse automat):
```bash
kubectl delete namespace seminar
```

Sau ștergeți întregul cluster:
```bash
kind delete cluster --name k8s-flask
```

---

## Exerciții Practice

<a name="exerciții-practice"></a>

### Exercițiul 1: Deploy complet și verificare

Reporniți de la zero: creați clusterul, construiți și încărcați imaginea, aplicați toate manifestele în ordine.

1. Creați clusterul `k8s-flask` și încărcați `flask-redis-app:v1`.
2. **Cerință:** Aplicați manifestele în ordine numerică (`00-` → `04-`) și verificați cu `kubectl get all -n seminar` că toate resursele sunt create (2 Deployments, 2 Services, 3 Pod-uri Flask + 1 Pod Redis). Cât timp a durat până toate pod-urile Flask au ajuns în starea `1/1 READY`?
3. Accesați aplicația în browser și faceți 10 reîmprospătări. Notați câte pod-uri diferite au servit cererile.

### Exercițiul 2: Modificarea configurației prin ConfigMap

Una dintre valorile ConfigMap-ului este `APP_TITLE` — titlul afișat în pagina web.

1. **Cerință:** Editați `01-configmap.yaml` și schimbați `APP_TITLE` la `"Rețele de Calculatoare 2025 — Laborator K8s"`. Aplicați din nou cu `kubectl apply -f 01-configmap.yaml`.
2. Observați că pagina web **nu s-a schimbat** imediat — pod-urile existente nu sunt repornite automat când un ConfigMap se modifică. **Cerință:** Forțați repornirea pod-urilor Flask fără să modificați YAML-ul Deployment-ului:
   ```bash
   kubectl rollout restart deployment/flask-deployment -n seminar
   ```
3. Accesați din nou pagina și verificați că titlul s-a actualizat.


### Exercițiul 3: Inspecția Secretelor și discuție de securitate

1. Rulați: `kubectl get secret flask-secret -n seminar -o yaml` și copiați valoarea din câmpul `REDIS_PASSWORD`.
2. **Cerință:** Decodificați valoarea folosind comanda `echo "<valoarea copiată>" | base64 --decode`. Ce parolă vedeți?
3. Acum intrați într-un pod Flask cu `kubectl exec` și rulați `env | grep REDIS_PASSWORD`. Parola apare în clar?
4. **Discuție:** Dacă un atacator obține acces la cluster (sau la fișierul `~/.kube/config`), poate citi toate Secretele. Cercetați ce este [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) și explicați în 2-3 propoziții cum rezolvă această problemă.

### Exercițiul 4: DNS intern și debugging cu `kubectl exec`

Kubernetes oferă un sistem DNS intern — fiecare Service primește automat un nume DNS rezolvabil din orice Pod.

1. Intrați într-un shell interactiv în unul dintre pod-urile Flask:
   ```bash
   kubectl exec -it deployment/flask-deployment -n seminar -- bash
   ```
2. **Cerință:** Din interiorul containerului, verificați că puteți rezolva DNS-ul intern:
   ```bash
   # Forma scurtă
   curl http://redis-service:6379
   # Forma completă (FQDN)
   curl http://redis-service.seminar.svc.cluster.local:6379
   ```
   Redis va răspunde cu `-ERR wrong number of arguments` — este normal! Înseamnă că conexiunea TCP a reușit.
3. Verificați variabilele de mediu injectate: `env | grep -E "REDIS|APP_TITLE|NODE"`. Identificați care variabile vin din ConfigMap, care din Secret și care din `fieldRef`.
4. **Cerință:** Fără a ieși din container, rulați `curl http://localhost:5000/health/ready`. Ce răspuns primiți? Ce înseamnă?

---

### Exercițiul 5: IP-urile pod-urilor — subnetting, comunicare directă și de ce există Service-urile

În Kubernetes, **fiecare pod primește o adresă IP unică** din blocul de adrese al clusterului (Pod CIDR). Aceasta este o adresă IP reală, rutabilă în interiorul clusterului — nu o adresă virtuală. Există trei categorii distincte de adrese IP în cluster, cu roluri complet diferite.

**Pasul 1:** Listați toate adresele IP din namespace-ul `seminar`:

```bash
# IP-urile pod-urilor (Pod CIDR, ex: 10.244.x.x)
kubectl get pods -o wide -n seminar

# IP-urile Service-urilor (Service CIDR / ClusterIP, ex: 10.96.x.x)
kubectl get services -n seminar

# IP-ul nodului (adresa nodului Docker, ex: 172.18.0.x)
kubectl get nodes -o wide
```

Notați cele trei tipuri de adrese și observați că aparțin unor **subrețele diferite** (uitati-va la al doilea octet, ar trebui sa fie diferit). Completați tabelul:

| Resursă | Adresă IP | Subnet (CIDR) | Tip |
|---|---|---|---|
| Pod `flask-deployment-xxx` | ? | ? | Pod IP (efemer) |
| Pod `redis-deployment-xxx` | ? | ? | Pod IP (efemer) |
| Service `redis-service` | ? | ? | ClusterIP (virtual, stabil) |
| Service `flask-service` | ? | ? | ClusterIP (virtual, stabil) |
| Node `k8s-flask-control-plane` | ? | ? | Node IP |


```bash
kubectl get nodes k8s-flask-control-plane -o jsonpath='{.spec.podCIDR}'
```

Eu obtin subnetul: 10.244.0.0/24

Faceti screenshot cu tabelul. 

**Pasul 2:** Lansați un pod de debugging cu `nicolaka/netshoot` — o imagine specializată pentru diagnosticarea rețelei, care conține `ip`, `ping`, `tcpdump`, `curl`, `nslookup` și alte unelte:

```bash
kubectl run netshoot --image=nicolaka/netshoot -it --rm -n seminar --restart=Never -- bash
```

Din interiorul acestui pod, investigați interfețele de rețea și tabela de rutare:

```bash
# Adresa IP a pod-ului curent și interfața de rețea
ip addr show eth0

# Tabela de rutare
ip route

# Observați:
# - adresa IP a pod-ului (din Pod CIDR, ex: 10.244.x.y)
# - gateway-ul implicit (adresa bridge-ului de pe nod, ex: 10.244.x.1)
# - ruta pentru întregul Pod CIDR (ex: 10.244.0.0/16 via 10.244.x.1)
```

> **De ce traficul trece prin gateway chiar și între pod-uri de pe același nod?**
> Fiecare pod este izolat într-un network namespace propriu — practic o "cutie" separată cu propria interfață `eth0`, ca și cum ar fi o mașină distinctă. Pod-urile nu se "văd" direct între ele la nivel de interfață, deci orice pachet care iese din pod urmează singura rută disponibilă: spre gateway-ul de pe nod (un bridge virtual). Nodul preia pachetul și îl livrează la destinație — fie local, fie pe alt nod — aplicând pe drum regulile `iptables` pentru traducerea Service IP → Pod IP. Efectul secundar util este că tot traficul inter-pod trece printr-un singur punct de control. 

**Pasul 3:** Comunicare directă pod-to-pod prin IP, fără Service și fără DNS.

Obțineți IP-ul pod-ului Redis:

```bash
# Rulat din afara containerului (un alt terminal)
REDIS_POD_IP=$(kubectl get pod -l app=redis -n seminar -o jsonpath='{.items[0].status.podIP}')
echo "Redis Pod IP: $REDIS_POD_IP"
```

Din interiorul pod-ului `netshoot`, conectați-vă direct la IP-ul Redis, ocolind complet Service-ul și DNS-ul:

```bash
# Înlocuiți <REDIS_POD_IP> cu valoarea obținută mai sus
curl <REDIS_POD_IP>:6379

# Răspunsul așteptat este una din variantele:
#   curl: (52) Empty reply from server   → conexiune TCP reușită, Redis a închis-o (nu vorbește HTTP)
#   -ERR wrong number of arguments       → Redis a procesat cererea ca o comandă invalidă
# Ambele confirmă că traficul IP direct pod-to-pod funcționează.
# Dacă Redis nu ar fi accesibil, ai primi: "Connection refused" sau timeout.
```

**Pasul 4:** Demonstrarea instabilității IP-urilor de pod.

Forțați repornirea pod-ului Redis — pod-ul va fi șters și recreat, primind un **nou IP**:

```bash
kubectl rollout restart deployment/redis-deployment -n seminar
kubectl get pods -o wide -n seminar -w
# Urmăriți: IP-ul noului pod Redis este diferit față de cel vechi
```

Verificați că Service-ul `redis-service` (ClusterIP) **nu s-a schimbat**:

```bash
kubectl get service redis-service -n seminar
```

**Cerință:** Acesta este motivul pentru care Service-urile există. Scrieți un scurt paragraf care explică: de ce o arhitectură care s-ar baza pe IP-urile directe ale pod-urilor în loc de Service-uri ar fi fragilă în producție?

---


# Capitolul X9: Kubernetes în Producție — Microservicii, Bază de Date și Scalare pe Trafic

Până acum am rulat o singură aplicație (X7) și apoi am adăugat Redis ca serviciu partajat (X8). Aplicațiile reale de producție sunt compuse din **microservicii independente** care comunică prin rețea: un frontend care servește interfața, un API care conține logica de business, și o bază de date relațională care persistă datele.

În acest capitol construim o aplicație completă de gestionare a notițelor de curs cu arhitectură pe trei niveluri (*3-tier*), și introducem ultimele concepte esențiale de Kubernetes:

- **PersistentVolumeClaim (PVC)** — stocare persistentă pentru baza de date, supraviețuiește repornirii pod-urilor
- **Init Containers** — asigură că un serviciu pornește doar după ce dependențele sale sunt gata
- **Horizontal Pod Autoscaler (HPA)** — scalare automată pe baza traficului real (CPU)
- **Microservices best practices** — separarea responsabilităților, comunicare prin API intern
- **OpenLens pentru monitorizarea traficului** — vizualizare în timp real a scalării automate

## Cuprins

- [Arhitectura aplicației](#arhitectura-aplicației)
- [Concepte Noi](#concepte-noi)
- [Pasul 0: Pregătirea mediului](#pasul-0-pregătirea-mediului)
- [Pasul 1: Construirea imaginilor Docker](#pasul-1-construirea-imaginilor-docker)
- [Pasul 2: Deployarea în ordine](#pasul-2-deployarea-în-ordine)
- [Pasul 3: Init Container — startup ordonat](#pasul-3-init-container--startup-ordonat)
- [Pasul 4: PVC — de ce supraviețuiesc datele](#pasul-4-pvc--de-ce-supraviețuiesc-datele)
- [Pasul 5: Testarea aplicației](#pasul-5-testarea-aplicației)
- [Pasul 6: Instalarea Metrics Server](#pasul-6-instalarea-metrics-server)
- [Pasul 7: HPA — scalare automată pe trafic](#pasul-7-hpa--scalare-automată-pe-trafic)
- [Pasul 8: Monitorizare cu OpenLens](#pasul-8-monitorizare-cu-openlens)
- [Pasul 9: Curățarea mediului](#pasul-9-curățarea-mediului)
- [Exerciții Practice](#exerciții-practice)

---

## Arhitectura aplicației

```
                          Namespace: laborator
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                                                                         │
 │   Browser                                                               │
 │      │                                                                  │
 │      ▼  NodePort :30900                                                 │
 │  ┌───────────────────┐   HTTP (ClusterIP)   ┌─────────────────────┐    │
 │  │ frontend-service  │ ──────────────────── │    api-service      │    │
 │  │  (2 replici)      │   api-service:5001   │    (2-8 replici)    │    │
 │  │  Flask + Jinja2   │                      │    Flask REST API   │    │
 │  └───────────────────┘                      └──────────┬──────────┘    │
 │                                                        │               │
 │                                             ClusterIP  │  :5432        │
 │                                                        ▼               │
 │                                          ┌─────────────────────────┐   │
 │                                          │   postgres-service      │   │
 │                                          │   (1 replică)           │   │
 │                                          │   PostgreSQL 15         │   │
 │                                          │   + PVC (1Gi)           │   │
 │                                          └─────────────────────────┘   │
 │                                                                         │
 │   HPA → scalează automat api-deployment între 2 și 8 replici           │
 └─────────────────────────────────────────────────────────────────────────┘
```

**Principii de microservicii respectate:**
- **Separarea responsabilităților**: frontend → UI, api → logica de business + DB, postgres → persistență
- **Baza de date nu este niciodată expusă exterior** (ClusterIP) — accesibilă doar din API
- **API-ul nu este expus direct în browser** (ClusterIP) — accesat doar de frontend
- **Un singur punct de intrare** (frontend NodePort) — simplitate și securitate

---

## Concepte Noi

| Concept | Ce face |
|---|---|
| **PersistentVolumeClaim (PVC)** | Solicită spațiu de stocare persistent din cluster. Datele supraviețuiesc ștergerii/repornirii pod-ului. |
| **PersistentVolume (PV)** | Volumul real de stocare creat automat de KinD (local path pe nod). |
| **Init Container** | Container care rulează *înainte* de cel principal. Trebuie să se termine cu succes. Folosit pentru așteptarea dependențelor. |
| **HPA** | Monitorizează metrici (CPU/memorie) și ajustează automat numărul de replici între `minReplicas` și `maxReplicas`. |
| **Metrics Server** | Componentă Kubernetes care colectează metrici de utilizare resurse din noduri și pod-uri. Necesar pentru HPA și `kubectl top`. |
| **3-tier architecture** | Pattern: prezentare (frontend) → logică (api) → date (db). Fiecare nivel se scalează independent. |

---

## Pasul 0: Pregătirea mediului

<a name="pasul-0"></a>

Creați un cluster KinD proaspăt (sau reutilizați pe cel existent):

```bash
kind create cluster --name k8s-notes
kubectl cluster-info --context kind-k8s-notes
```

---

## Pasul 1: Construirea imaginilor Docker

<a name="pasul-1"></a>

Avem două imagini custom de construit: **frontend** și **api**. PostgreSQL este oficial și va fi descărcat automat de KinD.

```bash
# Imaginea frontend
cd frontend
docker build -t notes-frontend:v1 .

# Imaginea API
cd ../api
docker build -t notes-api:v1 .
```

Încărcați ambele imagini în cluster:
```bash
kind load docker-image notes-frontend:v1 --name k8s-notes
kind load docker-image notes-api:v1 --name k8s-notes
```

Verificați că sunt disponibile în nod:
```bash
docker exec -it k8s-notes-control-plane crictl images | grep notes
```

---

## Pasul 2: Deployarea în ordine

<a name="pasul-2"></a>

Ordinea contează: baza de date trebuie să existe înainte de API, care trebuie să existe înainte de frontend. Manifestele sunt numerotate tocmai pentru a impune această ordine.

```bash
cd ../k8s

kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secret.yaml
kubectl apply -f 03-postgres.yaml

# Așteptați ca PostgreSQL să fie Ready înainte de a continua
kubectl wait --for=condition=ready pod -l app=postgres -n laborator --timeout=90s

kubectl apply -f 04-api.yaml
kubectl apply -f 05-frontend.yaml
```

Verificați că toate resursele sunt create:
```bash
kubectl get all -n laborator
```

*(Expected output: 3 Deployments, 3 Services, 1 PVC, pod-uri în Running.)*

---

## Pasul 3: Init Container — startup ordonat

<a name="pasul-3"></a>

Deschideți `04-api.yaml` și observați secțiunea `initContainers`. Aceasta definește un container `wait-for-postgres` care rulează `nc -z postgres-service 5432` în buclă până când PostgreSQL acceptă conexiuni TCP.

Vizualizați procesul de init în timp real:
```bash
kubectl get pods -n laborator -w
# Observați starea: Init:0/1 → PodInitializing → Running
```

Vedeți log-urile init container-ului:
```bash
# Înlocuiți <pod-name> cu un pod api real
kubectl logs <pod-name> -c wait-for-postgres -n laborator
```

> **De ce este important?** Fără init container, API-ul ar porni, ar eșua la conectarea la DB, ar fi repornit de Kubernetes, și tot ciclul s-ar repeta (CrashLoopBackOff). Init container-ul elimina complet această problemă: nu pornește niciodată procesul principal dacă dependința nu este disponibilă.

---

## Pasul 4: PVC — de ce supraviețuiesc datele

<a name="pasul-4"></a>

Analizați `03-postgres.yaml`. Conține trei obiecte:
1. **PersistentVolumeClaim** — cerere de spațiu de stocare (`1Gi`)
2. **Deployment** — montează PVC-ul la `/var/lib/postgresql/data`
3. **Service** — ClusterIP intern

```bash
# Vizualizați PVC-ul și volumul asociat
kubectl get pvc -n laborator
kubectl get pv   # PersistentVolume creat automat de KinD
```

**Experimentul de persistență:**
```bash
# 1. Adăugați câteva note în aplicație prin browser

# 2. Ștergeți pod-ul PostgreSQL
kubectl delete pod -l app=postgres -n laborator

# 3. Urmăriți cum Kubernetes recreează pod-ul
kubectl get pods -n laborator -w

# 4. Accesați din nou aplicația — notele sunt intacte!
```

> **De ce datele supraviețuiesc?** Pod-ul a fost recreat, dar PVC-ul (și PV-ul asociat) rămân. Noul pod montează același volum la pornire. Acesta este motivul fundamental pentru care bazele de date din Kubernetes au nevoie de PVC — fără el, datele s-ar pierde la orice repornire de pod.

---

## Pasul 5: Testarea aplicației

<a name="pasul-5"></a>

Obțineți IP-ul nodului:
```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "Aplicație: http://$NODE_IP:30900"
```

Sau folosiți port-forward:
```bash
kubectl port-forward service/frontend-service 5000:5000 -n laborator
# Deschideți http://localhost:5000
```

**Ce puteți observa în aplicație:**
- Panoul din stânga-jos arată care **pod frontend** a servit cererea 
- **API Status** — confirmă că frontend-ul comunică cu API-ul
- Adăugați și ștergeți note — sunt stocate în PostgreSQL și persistă la reîmprospătare

**Testați API-ul direct:**
```bash
# Listați notele (prin port-forward sau din interiorul unui pod)
curl http://$NODE_IP:30900  # prin frontend

# Sau direct API-ul din interiorul clusterului
kubectl run test-curl --image=curlimages/curl -it --rm -n laborator \
  -- curl http://api-service:5001/notes
```

---

## Pasul 6: Instalarea Metrics Server

<a name="pasul-6"></a>

HPA are nevoie de **Metrics Server** pentru a colecta datele de CPU/memorie. KinD nu îl include implicit.

```bash
# Instalați metrics-server (versiunea upstream)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# KinD nu are certificate TLS valide pe Kubelet — adăugăm flag-ul necesar
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# Așteptați ca metrics-server să fie Ready (~30 secunde)
kubectl rollout status deployment/metrics-server -n kube-system

# Verificați că funcționează
kubectl top nodes
kubectl top pods -n laborator
```

*(Dacă `kubectl top` returnează eroare, așteptați 1-2 minute — metrics-server are nevoie de timp pentru a colecta primele date.)*

---

## Pasul 7: HPA — scalare automată pe trafic

<a name="pasul-7"></a>

### Activarea HPA

```bash
kubectl apply -f 06-hpa.yaml
kubectl get hpa -n laborator
```

Veți vedea ceva de forma:
```
NAME      REFERENCE                    TARGETS   MINPODS   MAXPODS   REPLICAS
api-hpa   Deployment/api-deployment   5%/50%    2         8         2
```

`TARGETS` arată utilizarea curentă vs. pragul de scalare (50% CPU).

### Generarea de trafic artificial

Deschidem un pod temporar care face cereri continue la API pentru a ridica utilizarea CPU:

```bash
# Într-un terminal separat — generează trafic
kubectl run load-generator --image=busybox:1.36 -n laborator --rm -it -- /bin/sh -c \
  "while true; do wget -q -O- http://api-service:5001/notes > /dev/null; done"
```

Urmăriți scalarea în timp real într-un alt terminal:
```bash
# Vedeți HPA-ul ajustând numărul de replici
kubectl get hpa -n laborator -w

# Vedeți pod-urile noi apărând
kubectl get pods -n laborator -w
```

Opriți load generator-ul cu **Ctrl+C**. După câteva minute (HPA are un cooldown implicit de 5 minute), veți vedea API-ul scalând înapoi la 2 replici.

> **Cum funcționează HPA?** La fiecare 15 secunde, Metrics Server raportează utilizarea medie CPU per pod din `api-deployment`. Dacă media depășește 50% din valoarea `requests.cpu`, HPA calculează câte replici sunt necesare: `replici_noi = ceil(replici_curente × (utilizare_curentă / utilizare_țintă)`. Exemplu: 2 replici la 80% CPU → `ceil(2 × 80/50)` = 4 replici.

---

## Pasul 8: Monitorizare cu OpenLens

<a name="pasul-8"></a>

OpenLens oferă o vizualizare în timp real a scalării pe care terminalul nu o poate egala.

### Setup

Deschideți OpenLens și conectați-vă la `kind-k8s-notes`. Selectați namespace-ul `laborator` din dropdown.

### Ce să urmăriți în timp ce HPA scalează

1. **Workloads → Pods** — urmăriți pod-urile `api-*` apărând și dispărând în timp real pe măsură ce HPA lucrează

2. **Workloads → Deployments → api-deployment** — panoul de detalii arată:
   - `Desired Replicas` vs `Ready Replicas`
   - Condiția `Progressing` în timp ce pod-urile sunt create

3. **Workloads → HPA** (sau **Autoscalers**) — vedeți în timp real:
   - `Current Replicas` / `Desired Replicas`
   - Utilizarea medie CPU vs. pragul configurat

4. **Nodes → k8s-notes-control-plane** — consumul de CPU al nodului KinD, care crește vizibil sub sarcină

### Scalare manuală din OpenLens

Puteți scala manual fără a folosi terminalul:
1. Mergeți la **Workloads → Deployments → frontend-deployment**
2. Click pe iconița cu creion (Edit) sau butonul Scale
3. Schimbați `replicas` la `4` și salvați
4. Reveniți la **Pods** și urmăriți pod-urile noi intrând în starea `Running`

### Vizualizarea traseului unei cereri (tracing manual)

1. Deschideți aplicația în browser și adăugați o notă
2. În OpenLens, deschideți log-urile unui pod `api-*` (click pe pod → tab **Logs**)
3. Veți vedea log-ul intrării `POST /notes` exact în pod-ul care a servit cererea
4. Reîncercați — de data aceasta cererea poate fi servită de alt pod (load balancing)

---

## Pasul 9: Curățarea mediului

<a name="pasul-9"></a>

```bash
# Ștergeți namespace-ul (toate resursele din el, inclusiv PVC, sunt șterse)
kubectl delete namespace laborator

# Ștergeți clusterul complet
kind delete cluster --name k8s-notes
```

> **Atenție:** Ștergerea namespace-ului include ștergerea PVC-ului și a datelor din baza de date! Acesta este comportamentul corect pentru un cluster de laborator. Într-un mediu de producție, PVC-urile cu date importante ar fi protejate cu `Reclaim Policy: Retain`.

---

## Exerciții Practice

<a name="exerciții-practice"></a>

### Exercițiul 1: Deploy complet și verificarea arhitecturii

Deployați întreaga aplicație de la zero și verificați că toate componentele comunică corect.

1. **Cerință:** Construiți imaginile, creați clusterul, încărcați imaginile, aplicați manifestele în ordine. Verificați cu `kubectl get all -n laborator` că aveți 3 Deployments, 3 Services, 1 PVC și că toate pod-urile sunt `Running` și `1/1 READY`.
2. Accesați aplicația în browser și adăugați 3 note cu titluri diferite. Reîmprospătați pagina de mai multe ori.
Atasati screenshot.

### Exercițiul 2a: Investigarea Init Container-ului

Init container-ul din `04-api.yaml` implementează un pattern clasic de *dependency waiting*.

1. Scalați PostgreSQL la 0 replici: `kubectl scale deployment/postgres-deployment --replicas=0 -n laborator`
2. Scalați API-ul la 0, apoi înapoi la 2: `kubectl scale deployment/api-deployment --replicas=0 -n laborator && kubectl scale deployment/api-deployment --replicas=2 -n laborator`
3. **Cerință:** Urmăriți cu `kubectl get pods -n laborator -w` tranziția prin stările `Init:0/1` → `PodInitializing` → `Running`. Cât timp a stat pod-ul în starea de Init?
4. Reporniți PostgreSQL (`replicas=1`) și observați că pod-urile API trec automat în `Running`.
Atasati screenshot cu terminalul.

### Exercițiul 2b: Investigarea Init Container-ului
5. **Discuție:** Ce alternativă la init containers există? Cercetați conceptul de [readiness gates](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-readiness-gate). 
Descrieti ce este si diferentele principale. 

### Exercițiul 3: Demonstrarea persistenței datelor cu PVC

PersistentVolumeClaim este ceea ce separă o bază de date funcțională de una care pierde datele la orice repornire.

1. Adăugați minimum 5 note prin interfață.
2. **Cerință:** Ștergeți pod-ul PostgreSQL: `kubectl delete pod -l app=postgres -n laborator`. Urmăriți cu `kubectl get pods -n laborator -w` cum Kubernetes recreează pod-ul.
3. Accesați aplicația — notele sunt intacte?
4. **Cerință:** Acum ștergeți **PVC-ul**: `kubectl delete pvc postgres-pvc -n laborator`. Ce se întâmplă cu pod-ul PostgreSQL? (PostgreSQL nu va mai porni fără volum.) Recreați PVC-ul: `kubectl apply -f k8s/03-postgres.yaml`. Sunt notele recuperate?
5. **Discuție:** De ce datele s-au pierdut la ștergerea PVC-ului dar nu la ștergerea pod-ului? Ce este un `ReclaimPolicy` și cum ar ajuta în producție?
Raspundeti la intrebari in text. 

### Exercițiul 4: Scalarea independentă a microserviciilor

Un avantaj cheie al arhitecturii microservicii este că fiecare componentă se scalează independent.

1. Deschideți un terminal cu `kubectl get pods -n laborator -w` pentru a urmări în timp real.
2. **Cerință:** Scalați **doar frontend-ul** la 5 replici. Câte pod-uri API și PostgreSQL există? (Răspunsul așteptat: numărul rămâne neschimbat — fiecare nivel se scalează independent.)
3. Folosiți `kubectl exec -it <pod-frontend> -n laborator -- bash` și din interiorul containerului, apelați API-ul direct: `curl http://api-service:5001/notes | python3 -m json.tool`. Ce vedeți?
4. **Cerință:** Acum scalați **doar API-ul** la 4 replici și generați trafic din browser (adăugați/ștergeți note rapid).
Adaugati screenshot. 

### Exercițiul 5a: HPA în acțiune cu OpenLens

Scalarea automată bazată pe trafic este una dintre cele mai valoroase funcționalități Kubernetes.

1. Asigurați-vă că Metrics Server este instalat și funcționează (`kubectl top pods -n laborator`).
2. Aplicați `06-hpa.yaml` și verificați cu `kubectl get hpa -n laborator`.
3. **Cerință:** Deschideți OpenLens → namespace `laborator` → Workloads → HPA (`api-hpa`). Porniți load generator-ul din Pasul 7 al ghidului. Urmăriți în OpenLens cum cresc `Current Replicas` pe măsură ce CPU urcă. Faceți screenshot la HPA-ul cu mai mult de 2 replici.
Atasati screenshot. 

### Exercițiul 5b: HPA în acțiune cu OpenLens
4. Opriți load generator-ul. Așteptați 5-10 minute. **Cerință:** Observați HPA-ul scalând **înapoi** la 2 replici (scale-down cooldown). Cât timp a durat?
5. **Discuție:** HPA-ul nu scalează automat PostgreSQL — de ce? Ce soluții există pentru scalarea orizontală a bazelor de date relaționale în Kubernetes? *(Indiciu: cercetați `CockroachDB`, `Vitess`, sau `CloudNativePG`.)*
Descrieti ce este si diferentele principale. 

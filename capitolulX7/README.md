# Capitolul X7: Introducere în Kubernetes cu KinD

Tema este aici: https://docs.google.com/forms/d/e/1FAIpQLSePUt0o3W4JAz6jVsA3fm-gmT6JZbEWtlnFMYia7GmH2iDXFQ/viewform?usp=publish-editor


**Kubernetes** este platforma open-source standard industrial pentru orchestrarea containerelor. Dacă Docker ne permite să împachetăm o aplicație într-un container, Kubernetes ne permite să rulăm, să scalăm și să gestionăm sute de astfel de containere pe un cluster de mașini, asigurând disponibilitate ridicată și recuperare automată din defecțiuni.

În acest capitol vom folosi **KinD (Kubernetes in Docker)** — un instrument care creează un cluster Kubernetes complet funcțional chiar în interiorul containerelor Docker de pe mașina voastră locală. 

În folderul `flask-app/` găsiți o aplicație Python/Flask simplă alături de `Dockerfile`-ul său, iar în folderul `k8s/` găsiți manifestele Kubernetes care descriu cum să fie rulată în cluster.

## Cuprins

- [Concepte Cheie](#concepte-cheie)
- [Pasul 0: Instalarea instrumentelor necesare](#pasul-0-instalarea-instrumentelor-necesare)
- [Pasul 1: Construirea imaginii Docker](#pasul-1-construirea-imaginii-docker)
- [Pasul 2: Crearea clusterului KinD și încărcarea imaginii](#pasul-2-crearea-clusterului-kind-și-încărcarea-imaginii)
- [Pasul 3: Deployarea aplicației (Deployment)](#pasul-3-deployarea-aplicației-deployment)
- [Pasul 4: Expunerea aplicației (Service)](#pasul-4-expunerea-aplicației-service)
- [Pasul 5: Scalarea aplicației](#pasul-5-scalarea-aplicației)
- [Pasul 6: Experimentul Haos — Auto-Vindecarea](#pasul-6-experimentul-haos--auto-vindecarea)
- [Pasul 7: Explorare vizuală cu OpenLens](#pasul-7-explorare-vizuală-cu-openlens)
- [Pasul 8: Curățarea mediului](#pasul-8-curățarea-mediului)
- [Exerciții Practice](#exerciții-practice)

---

## Concepte Cheie

Înainte de a începe, familiarizați-vă cu vocabularul Kubernetes:

| Concept | Descriere |
|---|---|
| **Cluster** | Grupul de mașini (reale sau virtuale) pe care Kubernetes le gestionează. Are un **Control Plane** (creierul) și **Node-uri** (unde rulează aplicațiile). |
| **Pod** | Cea mai mică unitate din Kubernetes. Un Pod conține unul sau mai multe containere care partajează rețeaua și stocarea. În general, un Pod = un container. |
| **Deployment** | Un obiect care descrie *starea dorită*: "vreau 2 replici ale containerului X, mereu în funcțiune". Kubernetes se asigură că realitatea corespunde întotdeauna cu această descriere. |
| **Service** | Un obiect care oferă o adresă de rețea stabilă și balansare de sarcină (*load balancing*) pentru un grup de Pod-uri. Pod-urile pot dispărea și reapărea, dar Service-ul are mereu același IP/port. |
| **Manifest YAML** | Fișierul text în care descriem obiectele Kubernetes (Deployment, Service etc.). Îl aplicăm cu `kubectl apply -f`. |
| **`kubectl`** | Unealta din linia de comandă pentru a interacționa cu clusterul Kubernetes. |
| **KinD** | *Kubernetes in Docker* — rulează nodurile unui cluster Kubernetes ca simple containere Docker pe calculatorul vostru. |

---

## Pasul 0: Instalarea instrumentelor necesare

Asigurați-vă că aveți instalate pe mașina locală:

- **Docker** (trebuie să ruleze)
- **KinD**: Urmați instrucțiunile de la [kind.sigs.k8s.io/docs/user/quick-start/#installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
  ```bash
  # Exemplu pentru macOS cu Homebrew:
  brew install kind
  ```
- **kubectl**: Unealta CLI pentru Kubernetes. Instrucțiuni la [kubernetes.io/docs/tasks/tools/](https://kubernetes.io/docs/tasks/tools/)
  ```bash
  # Exemplu pentru macOS cu Homebrew:
  brew install kubectl
  ```

Verificați că totul funcționează:
```bash
docker --version
kind --version
kubectl version --client
```

---

## Pasul 1: Construirea imaginii Docker

<a name="pasul-1"></a>

Aplicația din `flask-app/app.py` returnează un răspuns HTML care include:
- **Numele Pod-ului** care a servit cererea (variabila de mediu `HOSTNAME`, setată automat de Kubernetes)
- **Numele Node-ului** pe care rulează (injectat de Kubernetes prin `fieldRef`)
- **Numărul de cereri** servite de acel Pod specific

Construim imaginea Docker din directorul `flask-app/`:

```bash
cd flask-app
docker build -t my-flask-app:v1 .
```

Verificați că imaginea a fost creată cu succes:
```bash
docker images | grep my-flask-app
```

---

## Pasul 2: Crearea clusterului KinD și încărcarea imaginii

<a name="pasul-2"></a>

### Crearea clusterului

> **Important pentru macOS și Windows:** Docker Desktop rulează containerele într-o mașină virtuală Linux internă. Prin urmare, IP-urile nodurilor KinD (ex: `172.x.x.x`) **nu sunt accesibile direct din browser**. Pentru a putea accesa aplicația prin NodePort de pe mașina locală, trebuie să creați clusterul cu un fișier de configurare care mapează portul nodului la `localhost`.

Creați fișierul de configurare `kind-config.yaml` în directorul curent:
```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30500
        hostPort: 30500
        protocol: TCP
```

Apoi creați clusterul folosind această configurație:
```bash
kind create cluster --name k8s-flask --config kind-config.yaml
```

> **Fără `extraPortMappings`:** Dacă ați creat deja clusterul fără acest fișier, ștergeți-l cu `kind delete cluster --name k8s-flask` și recreați-l cu comanda de mai sus. Alternativ, folosiți întotdeauna `kubectl port-forward` (Varianta 1 de la Pasul 4).

*Primul start poate dura 1-2 minute, deoarece KinD descarcă imaginile nodurilor. Veți vedea `kindest/node` în `docker ps` după creare.*

Verificați că clusterul funcționează și că `kubectl` este configurat să comunice cu el:
```bash
kubectl cluster-info --context kind-k8s-flask
kubectl get nodes
```
*(Expected output: Un nod cu statusul `Ready`.)*

### Încărcarea imaginii în cluster

Kubernetes caută de obicei imaginile pe internet (Docker Hub, GHCR etc.). Deoarece `my-flask-app:v1` există **doar pe calculatorul vostru local**, trebuie să o "injectăm" manual în nodurile clusterului KinD:

```bash
kind load docker-image my-flask-app:v1 --name k8s-flask
```

> **De ce este necesar acest pas?**
> KinD rulează nodurile ca containere Docker izolate. Aceste containere nu au acces direct la lista de imagini de pe host-ul vostru — au propriul lor "magazin" de imagini. Comanda `kind load` copiază imaginea din host în interiorul fiecărui nod al clusterului.

---

## Pasul 3: Deployarea aplicației (Deployment)

<a name="pasul-3"></a>

Analizați fișierul `k8s/flask-app.yaml`. Prima secțiune descrie un `Deployment`:
- **`replicas: 2`** — Kubernetes va menține mereu 2 Pod-uri active
- **`selector`** și **`labels`** — mecanismul prin care Kubernetes știe ce Pod-uri aparțin acestui Deployment
- **`imagePullPolicy: IfNotPresent`** — îi spunem lui Kubernetes să folosească imaginea deja existentă în nod, nu să o descarce de pe internet
- **`env.NODE_NAME`** — un exemplu de `fieldRef`: Kubernetes injectează automat în containerul nostru numele nodului pe care rulează

Aplicați manifestul din directorul `k8s/`:
```bash
cd ../k8s
kubectl apply -f flask-app.yaml
```

Verificați că Pod-urile pornesc:
```bash
kubectl get pods
# Așteptați până când STATUS devine Running pentru ambele pod-uri
kubectl get pods -w  # flag-ul -w urmărește schimbările în timp real (Ctrl+C pentru a ieși)
```

Explorați un Pod mai în detaliu:
```bash
# Înlocuiți <nume-pod> cu un nume real din output-ul comenzii de mai sus
kubectl describe pod <nume-pod>
kubectl logs <nume-pod>
```

---

## Pasul 4: Expunerea aplicației (Service)

<a name="pasul-4"></a>

A doua secțiune din `flask-app.yaml` (după `---`) descrie un `Service` de tip **NodePort**:
- **`selector: app: flask-web`** — Service-ul trimite traficul spre orice Pod cu această etichetă
- **`nodePort: 30500`** — portul prin care puteți accesa aplicația de pe mașina locală

Serviciul a fost deja creat la pasul anterior (ambele obiecte sunt în același fișier YAML). Verificați:
```bash
kubectl get services
```

### Accesarea aplicației

**Port-forward (simplă, pentru testare rapidă)**

Creează un tunel direct de la portul local `5000` la Deployment:
```bash
kubectl port-forward deployment/flask-deployment 5000:5000
```
Deschideți browserul la `http://localhost:5000`. Apăsați `Ctrl+C` pentru a opri tunelul.


## Pasul 5: Scalarea aplicației

<a name="pasul-5"></a>

Unul dintre marile avantaje ale Kubernetes este scalarea cu o singură comandă. Să creștem numărul de replici de la 2 la 4:

```bash
kubectl scale deployment/flask-deployment --replicas=4
```

Observați în timp real cum Kubernetes creează noile Pod-uri:
```bash
kubectl get pods -w
```

Acum reîmprospătați pagina în browser — veți vedea 4 pod-uri diferite servind cererile!

Scalați înapoi la 2:
```bash
kubectl scale deployment/flask-deployment --replicas=2
```

---

## Pasul 6: Experimentul cu moartea unui pod - Auto-Vindecarea

<a name="pasul-6"></a>

Aceasta este una dintre caracteristicile definitorii ale Kubernetes: dacă un Pod moare, **Deployment-ul îl recreează automat** pentru a menține numărul dorit de replici.

Obțineți lista de Pod-uri:
```bash
kubectl get pods
```

Ștergeți unul dintre ele (înlocuiți cu un nume real):
```bash
kubectl delete pod <insert-one-pod-name-here>
```

Urmăriți ce se întâmplă:
```bash
kubectl get pods -w
```

Veți observa:
1. Pod-ul șters trece în starea `Terminating`
2. **Instant**, Kubernetes pornește un Pod nou pentru a-l înlocui (starea `ContainerCreating` → `Running`)
3. În câteva secunde, reveniți la 2 Pod-uri active

> **Ce s-a întâmplat?** Deployment-ul declară că starea dorită este `replicas: 2`. Kubernetes monitorizează permanent starea reală. Când a detectat că un Pod a dispărut, *Reconciliation Loop*-ul a acționat imediat pentru a readuce sistemul la starea dorită.

---

## Pasul 7: Explorare vizuală cu OpenLens

<a name="pasul-7-explorare-vizuală-cu-openlens"></a>

`kubectl` este puternic, dar poate fi dificil de urmărit când rulați mai multe comenzi simultan. **OpenLens** este o interfață grafică (GUI) gratuită și open-source pentru Kubernetes care vă permite să vizualizați tot ce se întâmplă în cluster — Pod-uri, Deployment-uri, Service-uri, log-uri — dintr-un singur ecran.

### Instalarea OpenLens

Descărcați cea mai recentă versiune de pe GitHub Releases:
[https://github.com/MuhammedKalkan/OpenLens/releases](https://github.com/MuhammedKalkan/OpenLens/releases)

Sau cu Homebrew pe macOS:
```bash
brew install --cask openlens
```

### Conectarea la clusterul KinD

KinD configurează automat `kubectl` să cunoască clusterul `k8s-flask`. OpenLens citește același fișier de configurare (`~/.kube/config`), deci clusterul va apărea automat.

1. Deschideți **OpenLens**.
2. În panoul din stânga veți vedea clusterul `kind-k8s-flask` listat automat.
3. Faceți click pe el pentru a vă conecta.

### Ce să explorați în interfață

Odată conectat, navigați prin meniurile din stânga:

| Secțiune | Ce veți vedea |
|---|---|
| **Workloads → Pods** | Lista tuturor Pod-urilor, starea lor (`Running`, `Pending`), Node-ul pe care rulează și vârsta lor. Click pe un Pod → tab-ul **Logs** pentru a vedea output-ul live al containerului. |
| **Workloads → Deployments** | Deployment-ul `flask-deployment` cu numărul curent de replici dorite vs. disponibile. |
| **Network → Services** | Service-ul `flask-service` de tip `NodePort` cu porturile configurate. |
| **Nodes** | Node-ul clusterului KinD cu resursele sale (CPU, memorie). |

### Experimentul vizual: scalare din interfață

1. Mergeți la **Workloads → Deployments** și faceți click pe `flask-deployment`.
2. În colțul din dreapta sus al panoului apăsați iconița cu creion (Edit) sau găsiți butonul de scalare.
3. Alternativ, puteți edita direct YAML-ul Deployment-ului schimbând `replicas` și salvând — OpenLens va aplica modificarea în cluster instant.
4. Reveniți la **Workloads → Pods** și urmăriți în timp real cum apar sau dispar Pod-urile.

> **De ce este util?** Interfața vizuală vă oferă o perspectivă de ansamblu imposibil de obținut cu comenzi CLI individuale. Veți înțelege mai ușor relațiile dintre obiecte: cum un Deployment controlează ReplicaSet-ul, care la rândul lui gestionează Pod-urile.

---

## Pasul 8: Curățarea mediului

<a name="pasul-8"></a>

La finalul sesiunii, ștergeți clusterul KinD. Aceasta oprește și șterge toate containerele Docker asociate (OpenLens va marca automat clusterul ca offline):

```bash
kind delete cluster --name k8s-flask
```

Verificați că nu mai există clustere active:
```bash
kind get clusters
```

---

## Exerciții Practice

<a name="exerciții-practice"></a>

### Exercițiul 1: Analiza fișierelor și construirea imaginii

Înainte de a deploya orice pe Kubernetes, avem nevoie de imaginea Docker a aplicației.

1. Deschideți fișierul `flask-app/app.py`. Identificați: ce informații returnează aplicația? De unde obține numele Pod-ului și al Node-ului?
2. Deschideți `flask-app/Dockerfile`. Ce comandă instalează dependențele Python?
3. **Cerință:** Construiți imaginea Docker cu tag-ul `my-flask-app:v1`, apoi creați clusterul KinD `k8s-flask` și încărcați imaginea în el. Verificați că imaginea este disponibilă în nod rulând `docker exec -it k8s-flask-control-plane crictl images | grep flask`. Atasati screenshot. 

### Exercițiul 2: Deployment și inspecția Pod-urilor

Acum că imaginea este în cluster, vom deploya aplicația.

1. Aplicați manifestul `k8s/flask-app.yaml` cu `kubectl apply`.
2. **Cerință:** Așteptați până când ambele Pod-uri sunt în starea `Running`. Alegeți un Pod și rulați `kubectl describe pod <nume-pod>`. Identificați în output: pe ce Node rulează Pod-ul? Ce variabile de mediu sunt configurate?
3. Rulați `kubectl logs <nume-pod>` pentru a vedea output-ul serverului Flask la pornire.
Atasati screenshot

### Exercițiul 3: Scalarea Deployment-ului

Kubernetes face scalarea trivială.

1. **Cerință:** Scalați Deployment-ul la **3 replici** folosind comanda `kubectl scale`. Verificați că există exact 3 Pod-uri în starea `Running`.
2. Folosind `kubectl port-forward deployment/flask-deployment 5000:5000`, accesați `http://localhost:5000` și reîmprospătați pagina de mai multe ori. Notați numele pod-urilor care apar.
3. **Cerință:** Scalați Deployment-ul înapoi la **2 replici** și observați cu `kubectl get pods -w` cum Kubernetes termină Pod-ul în exces.
Atasati screenshot cu 3 dovada ca replici ruleaza. 

### Exercițiul 4: Experimentul de Auto-Vindecare (Self-Healing)

Vom simula un crash al unui container pentru a vedea Kubernetes în acțiune.

1. Obțineți lista curentă de Pod-uri cu `kubectl get pods` și rețineți numele lor.
2. **Cerință:** Ștergeți unul dintre Pod-uri cu `kubectl delete pod <nume-pod>`. Imediat după, rulați `kubectl get pods -w` și observați în timp real cum este creat un Pod de înlocuire.
3. Răspundeți in text: Cât timp aproximativ a durat crearea noului Pod? Ce ar fi necesitat această operațiune manual, fără Kubernetes?

### Exercițiul 5: Explorare vizuală cu OpenLens

Uneltele CLI sunt esențiale, dar un dashboard vizual accelerează înțelegerea arhitecturii unui cluster.

1. Instalați **OpenLens** de pe [github.com/MuhammedKalkan/OpenLens/releases](https://github.com/MuhammedKalkan/OpenLens/releases) (sau `brew install --cask openlens` pe macOS).
2. Porniți aplicația. Clusterul `kind-k8s-flask` ar trebui să apară automat în lista de clustere (OpenLens citește `~/.kube/config`). Conectați-vă la el.
3. **Cerință:** Navigați la **Workloads → Pods**. Faceți screenshot: câte Pod-uri sunt afișate? Care este starea fiecăruia? Pe ce Node rulează?
4. Faceți click pe unul dintre Pod-uri și deschideți tab-ul **Logs**. Observați log-urile live ale serverului Flask.
5. **Cerință:** Folosind OpenLens (secțiunea **Workloads → Deployments**), editați Deployment-ul și schimbați `replicas` la `3`. Observați în panoul **Pods** cum apare un Pod nou. 
Atasati screenshot din openlens cand ati scalat la 3. 

### Exercițiul 6: Modificarea aplicației și re-deployarea (Rolling Update)

Vom face o schimbare în cod și vom vedea cum se face o actualizare (*rolling update*).

1. Modificați fișierul `flask-app/app.py`: schimbați textul din `<h1>` din `Hello from Kubernetes!` în `Hello from Kubernetes - v2!`.
2. Reconstruiți imaginea cu un tag nou: `docker build -t my-flask-app:v2 .`
3. Încărcați noua imagine în cluster: `kind load docker-image my-flask-app:v2 --name k8s-flask`
4. **Cerință:** Modificați câmpul `image` din `k8s/flask-app.yaml` de la `my-flask-app:v1` la `my-flask-app:v2` și aplicați din nou manifestul cu `kubectl apply -f flask-app.yaml`. Urmăriți cu `kubectl get pods -w` cum Kubernetes face un **rolling update** — înlocuiește Pod-urile vechi cu cele noi, câte unul, fără întreruperea serviciului. Verificați în browser că mesajul s-a schimbat. 
Atasati screenshot la terminal cu modificarile

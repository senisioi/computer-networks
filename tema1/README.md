# Tema 1

## Informatii tema
Tema va fi livrata sub forma unui link/URL de git. Sectiunea de mai jos **[Instructiuni git](https://github.com/senisioi/computer-networks/tree/master/tema1#git)** contine toate informatiile de care aveti nevoie pentru a crea un repository si pentru a uploada fisierele pe git. Daca intampinati orice fel de probleme sau erori, va rog sa-mi scrieti pe mail. In repository veti adauga cateva fisiere de log-uri si un *docker-compose.yml* dupa cum este explicat in cerintele de mai jos.
Link-ul catre repository il trimite pe mail cu subject "tema1 retele 2018 Prenume Nume GRUPA".
Deadline: **29 martie**. Orice zi de intarziere se penalizeaza cu un punct.

## Cerinte tema (1 p. oficiu)
#### 1. Creati o noua imagine (3p.)
La acest pas veti crea o noua imagine care va avea tag-ul **tema1**. Cel mai simplu e sa refolositi fisierul [Dockerfile](https://github.com/senisioi/computer-networks/blob/master/docker/Dockerfile) pe care sa-l modificati pentru a instala tcpdump (vezi sectiunea cu tcpdump din [laborator 1](https://github.com/senisioi/computer-networks/blob/master/laborator1/README.md#tcpdump_install)) apoi selectati userul default ca fiind *root*, nu rtuser. Pentru asta, trebuie sa adaugati la sfarsit de tot linia `USER root`, in felul acest toate containerele vor rula default cu root. Dati [build](https://docs.docker.com/engine/reference/commandline/build/) la imagine folosind tag-ul tema1. Comanda de build este explicata si in [primul readme](https://github.com/senisioi/computer-networks/blob/master/README.md).


#### 2. Creati o retea tnet2 si definiti patru servicii rt1, rt2, rt3 si rt4 (3p.)
Modificati [docker-compose.yml](https://github.com/senisioi/computer-networks/blob/master/docker-compose.yml) si creati reteaua *tnet2* cu urmatorul gateway: 1.2.3.4. Configurati un subnet potrivit (care sa mearga) pentru acest gateway. Atentie cand modificati fisierul sa va asigurati ca formatarea este corecta si ca nu aveti caractere '\t' tab inserate.
Creati 4 containere/servicii pe aceasta retea cu numele rt1, rt2, rt3 si rt4 care sa ruleze imaginea *tema1* construita la pasul anterior. Pentru configurarea unui serviciu, pe langa image, network, volumes, tty, puteti utiliza:

- [**command:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#command) care sa defineasca o comanda ce se va executa cand porneste containerul.
- [**sysctls:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#sysctls) prin care sa se specifice configuratii de [kernel de linux](https://en.wikipedia.org/wiki/Sysctl).
- [**depends_on:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#depends_on) prin care sa se specifice o ordine de lansare a containerelor. Este posibil ca un container (rt2) sa depinda de un alt container (rt1) pentru ca rt2 sa porneasca cu succes.

Adaugati **command** si **depends_on** astfel incat urmatoarele comenzi sa se execute cu succes:

- rt1 sa ruleze `tcpdump -nSt icmp` (scaneaza doar pachete de tipul ICMP/ping)
- rt2 sa ruleze `ping -s 4000 rt1` (rt2 trimite pachete ICMP de dimensiune 4000 octeti lui rt1)
- rt3 sa ruleze `ping rt1` (rt3 trimite pachete ICMP de dimensiune 64 octeti lui rt1)
- rt4 sa ruleze `ping -c 1 rt3` (rt4 trimite un pachet ICMP lui rt3)

In plus, modificati containerul rt3 pentru a bloca ping-urile prin adaugarea unei configurari sysclts. In [laborator1, sectiunea cu ping](https://github.com/senisioi/computer-networks/tree/master/laborator1#ping_block), aveti un astfel de exemplu care defineste sysctls pentru a bloca ping-urile.


#### 3. Creati reteaua tnet1 si definiti un serviciu tn1 (3p.)
Tot in fisierul *docker-compose.yml* adaugati o retea noua cu numele *tnet1*. Reteaua trebuie sa aiba definit un subnet restrictiv (prin notatia cu [slash](https://github.com/senisioi/computer-networks/tree/master/laborator1#exercitiu1)) care sa permita lansarea unui singur container. Folositi adrese cat mai diverse pentru gateway si subnet, incercati ca doua rezolvari ale temei sa nu aiba acealsi IP. 
Definiti si un nou serviciu cu numele *tn1* care sa utilizeze imaginea **baseimage** si care sa fie conectat doar la reteaua *tnet1*. Acest serviciu trebuie sa execute: `"bash -c 'echo \"- interfetele de retea:\" && ip addr && echo \"- gateway:\" && ip route show'"` care deschide un nou shell (bash) si afiseaza configuratiile de retea si gateway-ul folosind comanda [ip](https://www.cyberciti.biz/faq/linux-ip-command-examples-usage-syntax/).

Comanda anterioara este echivalenta cu urmatorul script de bash, unde [&&](https://stackoverflow.com/questions/4510640/what-is-the-purpose-of-in-a-shell-command) este utilizat pentru a executa comenzile una dupa alta:
```bash
echo "- interfetele de retea:"
ip addr
echo "- gateway:"
ip route show
```


## Porniti toate containerele 
Folosind `docker-compose up -d` porniti toate containerele pe care le-ati definit in fisierul docker-compose.yml.
Observati ca daca porniti toate containerele si rulati `docker ps`, serviciul *tn1* nu apare in lista. Asta pentru ca acele comenzi de shell si-au terminat executia iar container-ul s-a oprit. Incercati sa rulati `docker-compose ps` pentru a vedea si care a fost [exit statusul](https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html) acelor comenzi. Vedem ca pentru containerul tn1 avem `Exit 0`, adica comenzile au fost executate cu succes.
De asemenea se poate vedea ca dupa un timp si containerul rt4 apare ca fiind oprit cu statusul `Exit 1` ceea ce inseamna ca acel ping cu un singur pachet catre container-ul rt3 a esuat si a returnat statusul 1.

Pentru a testa comenzile sau pentru a vedea log-urile si output-ul containerelor, utilizati:
```bash
docker-compose logs tn1
docker-compose logs rt1
docker-compose logs rt2
docker-compose logs rt3 rt4
```

Sau puteti redirecta continutul log-urilor in fisiere separate pe care le puteti deschide ulterior:
```bash
docker-compose logs rt1 > logs_rt1.log
docker-compose logs rt2 > logs_rt2.log
docker-compose logs rt3 > logs_rt3.log
docker-compose logs rt4 > logs_rt4.log
docker-compose logs tn1 > logs_tn1.log
```


<a name="git"></a>
## Adaugati totul pe git
#### Instructiuni git
Daca nu ati mai lucrat cu git, puteti urma pasii:

1. Creati-va un cont pe [github.com](https://github.com/). Daca doriti, puteti folosi si alti provideri (gitlab, bitbucket etc.), dar pasii urmatori sunt pentru github.
1. Creati un nou [repository](https://help.github.com/articles/create-a-repo/) de git.
2. [Clonati-l](https://help.github.com/articles/cloning-a-repository/) in calculatorul vostru apoi dati cd in directorul clonat. Clonarea se face cu `git clone URL`, unde URL e link-ul catre repository.
3. Sa presupunem ca ati rezolvat tema, ati creat fisierle *docker-compose.yml* si cele care contin log-urile containerelor. Copiati fisierele de logs \*.log si docker-compose.yml in folderul unde ati clonat repository-ul vostru de pe git.
4. Adaugati fisierele in repository [folosind linia de comanda](https://help.github.com/articles/adding-a-file-to-a-repository-using-the-command-line/):

```bash
git add docker-compose.yml
git add logs_rt1.log logs_rt2.log logs_rt3.log logs_rt4.log
git add logs_tn1.log
git commit -m "Mesaj cu primul meu commit - am rezolvat tema!"
git push origin master
```



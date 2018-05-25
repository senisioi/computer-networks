# Tema 1

## Informații temă
Tema va fi livrată sub forma unui link/URL de git. Secțiunea de mai jos **[Instrucțiuni git](https://github.com/senisioi/computer-networks/tree/master/tema1#git)** conține toate informațiile de care aveți nevoie pentru a crea un repository și pentru a uploada fișierele pe git. Dacă întâmpinați orice fel de probleme sau erori, vă rog sa-mi scrieți pe mail. În repository veți adăuga cateva fișiere de log-uri și un *docker-compose.yml* după cum este explicat în cerințele de mai jos.
Link-ul către repository îl trimiteți pe mail cu subject "tema1 retele 2018 Prenume Nume GRUPA".
Deadline: **29 martie**. Orice zi de întârziere se penalizează cu un punct.

## Cerințe tema (1 p. oficiu)
#### 1. Creați o nouă imagine (3p.)
La acest pas veți crea o nouă imagine care va avea tag-ul **tema1**. Cel mai simplu e să refolosiți fișierul [Dockerfile](https://github.com/senisioi/computer-networks/blob/master/docker/Dockerfile) pe care să-l modificați pentru a instala tcpdump (vezi secțiunea cu tcpdump din [laborator 1](https://github.com/senisioi/computer-networks/blob/master/laborator1/README.md#tcpdump_install)) apoi selectați userul default ca fiind *root*, nu rtuser. Pentru asta, trebuie să adăugați la sfârșit de tot linia `USER root`, în felul acesta toate containerele vor rula default cu root. Dați [build](https://docs.docker.com/engine/reference/commandline/build/) la imagine folosind tag-ul tema1. Comanda de build este explicată și în [primul readme](https://github.com/senisioi/computer-networks/blob/master/README.md).


#### 2. Creați o rețea tnet2 și definiți patru servicii rt1, rt2, rt3 si rt4 (3p.)
Modificați [docker-compose.yml](https://github.com/senisioi/computer-networks/blob/master/docker-compose.yml) și creați reteaua *tnet2* cu următorul gateway: 1.2.3.4. Configurați un subnet potrivit (care să meargă) pentru acest gateway. Atenție când modificați fișierul să vă asigurați că formatarea este corectă și că nu aveți caractere '\t' tab inserate.
Creați 4 containere/servicii pe această rețea cu numele rt1, rt2, rt3 si rt4 care să ruleze imaginea *tema1* construită la pasul anterior. Pentru configurarea unui serviciu, pe lângă image, network, volumes, tty, puteți utiliza:

- [**command:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#command) care să definească o comandă ce se va executa când pornește containerul.
- [**sysctls:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#sysctls) prin care să se specifice configurații de [kernel de linux](https://en.wikipedia.org/wiki/Sysctl).
- [**depends_on:**](https://docs.docker.com/compose/compose-file/compose-file-v2/#depends_on) prin care să se specifice o ordine de lansare a containerelor. Este posibil ca un container (rt2) să depindă de un alt container (rt1) pentru ca rt2 să pornească cu succes.

Adăugați **command** și **depends_on** astfel încât următoarele comenzi să se execute cu succes:

- rt1 să ruleze `tcpdump -nSt icmp` (scanează doar pachete de tipul ICMP/ping)
- rt2 să ruleze `ping -s 4000 rt1` (rt2 trimite pachete ICMP de dimensiune 4000 octeti lui rt1)
- rt3 să ruleze `ping rt1` (rt3 trimite pachete ICMP de dimensiune 64 octeti lui rt1)
- rt4 să ruleze `ping -c 1 rt3` (rt4 trimite un pachet ICMP lui rt3)

În plus, modificați containerul rt3 pentru a bloca ping-urile prin adăugarea unei configurări sysclts. În [laborator1, secțiunea cu ping](https://github.com/senisioi/computer-networks/tree/master/laborator1#ping_block), aveți un astfel de exemplu care definește sysctls pentru a bloca ping-urile.


#### 3. Creați reteaua tnet1 și definiți un serviciu tn1 (3p.)
Tot în fișierul *docker-compose.yml* adăugați o rețea nouă cu numele *tnet1*. Rețeaua trebuie să aibă definit un subnet restrictiv (prin notația cu [slash](https://github.com/senisioi/computer-networks/tree/master/laborator1#exercitiu1)) care să permită lansarea unui singur container. Folosiți adrese cât mai diverse pentru gateway și subnet, încercați ca două rezolvări ale temei să nu aibă același IP. 
Definiși și un nou serviciu cu numele *tn1* care să utilizeze imaginea **baseimage** și care să fie conectat doar la rețeaua *tnet1*. Acest serviciu trebuie să execute: `"bash -c 'echo \"- interfetele de retea:\" && ip addr && echo \"- gateway:\" && ip route show'"` care deschide un nou shell (bash) și afișează configurațiile de rețea și gateway-ul folosind comanda [ip](https://www.cyberciti.biz/faq/linux-ip-command-examples-usage-syntax/).

Comanda anterioară este echivalenta cu următorul script de bash, unde [&&](https://stackoverflow.com/questions/4510640/what-is-the-purpose-of-in-a-shell-command) este utilizat pentru a executa comenzile una după alta:
```bash
echo "- interfețele de rețea:"
ip addr
echo "- gateway:"
ip route show
```


## Porniți toate containerele 
Folosind `docker-compose up -d` porniți toate containerele pe care le-ați definit în fișierul docker-compose.yml.
Observați că dacă porniți toate containerele și rulați `docker ps`, serviciul *tn1* nu apare în listă. Asta pentru că acele comenzi de shell și-au terminat execuția iar container-ul s-a oprit. Încercați să rulați `docker-compose ps` pentru a vedea și care a fost [exit statusul](https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html) acelor comenzi. Vedem că pentru containerul tn1 avem `Exit 0`, adică comenzile au fost executate cu succes.
De asemenea se poate vedea că dupa un timp și containerul rt4 apare ca fiind oprit cu statusul `Exit 1` ceea ce înseamnă că acel ping cu un singur pachet către container-ul rt3 a eșuat și a returnat statusul 1.

Pentru a testa comenzile sau pentru a vedea log-urile si output-ul containerelor, utilizați:
```bash
docker-compose logs tn1
docker-compose logs rt1
docker-compose logs rt2
docker-compose logs rt3 rt4
```

Sau puteți redirecta conținutul log-urilor în fișiere separate pe care le puteți deschide ulterior:
```bash
docker-compose logs rt1 > logs_rt1.log
docker-compose logs rt2 > logs_rt2.log
docker-compose logs rt3 > logs_rt3.log
docker-compose logs rt4 > logs_rt4.log
docker-compose logs tn1 > logs_tn1.log
```


<a name="git"></a>
## Adăugați totul pe git
#### Instrucțiuni git
Dacă nu ați mai lucrat cu git, puteți urma pasii:

1. Creați-vă un cont pe [github.com](https://github.com/). Dacă doriți, puteți folosi și alți provideri (gitlab, bitbucket etc.), dar pașii următori sunt pentru github.
1. Creați un nou [repository](https://help.github.com/articles/create-a-repo/) de git.
2. [Clonați-l](https://help.github.com/articles/cloning-a-repository/) în calculatorul vostru apoi dați cd în directorul clonat. Clonarea se face cu `git clone URL`, unde URL e link-ul către repository.
3. Să presupunem că ați rezolvat tema, ați creat fisierle *docker-compose.yml* și cele care conțin log-urile containerelor. Copiați fișierele de logs \*.log și docker-compose.yml în folderul unde ați clonat repository-ul vostru de pe git.
4. Adăugați fișierele în repository [folosind linia de comanda](https://help.github.com/articles/adding-a-file-to-a-repository-using-the-command-line/):

```bash
git add docker-compose.yml
git add logs_rt1.log logs_rt2.log logs_rt3.log logs_rt4.log
git add logs_tn1.log
git commit -m "Mesaj cu primul meu commit - am rezolvat tema!"
git push origin master
```



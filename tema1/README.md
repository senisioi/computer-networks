# Tema 1

## Informații temă
Tema va fi livrată sub forma unui link/URL de git. Secțiunea de mai jos **[Instrucțiuni git](https://github.com/senisioi/computer-networks/tree/master/tema1#git)** conține toate informațiile de care aveți nevoie pentru a crea un repository și pentru a uploada fișierele pe git. Dacă întâmpinați orice fel de probleme sau erori, vă rog sa-mi scrieți pe mail. În repository veți adăuga cateva fișiere de log-uri și un *docker-compose.yml* după cum este explicat în cerințele de mai jos.
Link-ul către repository îl trimiteți pe mail cu subject "tema1 retele 2019 Prenume Nume GRUPA".
Deadline: **TBA**. Orice zi de întârziere se penalizează cu un punct.



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



#Navod na použitie tohto pluginu
## Inštalácia ##

Stiahnuť z [Downloads](https://code.google.com/p/archivy-czsk/downloads/list) pre svoju platformu mipsel(Dreambox,..), sh4(IPbox,Kathrein,..) ipk balíček a nainštalovať cez ipkg/opkg alebo grafické rozhranie enigmy2 a následne ju reštartovať.

---

## Nastavenia ##

  * **Použiť prehrávač:**
    * **Štandardný prehrávač** - prehrávač bez žiadnych úprav, použiť ho pri problémami s ostatnými
    * **Upravený prehrávač** - podporuje prehrávanie tituliek, odporúčaná voľba pre sh4
    * **Mipsel prehrávač** - podporuje prehrávanie tituliek a umožnuje nastaviť veľkosť bufferu v KB, ako aj to, či sa má automaticky začať prehrávať pri jeho naplnení, odporúčaná voľba pre mipsel.

  * **Prehrávač s RTMP podporou** - odporúčané zapnúť pre mipsel - umožňuje pretáčat v tv archívoch

  * **Buffer pre TV archívy** - štandardná voľba je 20000ms

  * **Buffer pre Živé vysielanie** - štandardná voľba je 20000ms

  * **Prehrávať po** - určíme počet sekúnd po ktorých sa začne prehrávať relácia pri voľbe prehrávať a sťahovať.

  * **Data** - adresár do ktorého sa budú ukladať dáta archívov

  * **Titulky** - adresár, ktorý sa ná zobrazí pri voľbe externých tituliek

  * **Sťahovanie** - adresár do ktorého sa budú ukladať sťahované súbory

  * **CSFD - zapnúť/vypnúť cez tlačidlo 5 CSFD info**

  * **Debug** - pri výpise chyby v archívoch sa bude vytvárať log súbor v /tmp/ adresáry s popisom chyby

  * **Automatická kontrola aktualizácií archívov** - pri každom štarte pluginu kontrolovať aktuálnosť archívov.


---


## Archívy ##

### Nastavenia ###

Každý archív má svoje nastavenia, cez nastavenia sa je takisto možné dostať k changelog-u archívu, kde si je možné pozrieť aktuálny zoznam zmien v archíve.

### Záložky ###
Pre obľúbené relácie je možné vytvoriť záložky archívu prostredníctvom kontextového menu - [menu](menu.md) tlačidlo a vybrať - vytvoriť záložku.

### Sťahované súbory ###
Každý archív má určený adresár pre svoje sťahované súbory, ak chceme prehrávať súbor, ktorý sme stiahli je ho možné zobraziť otvorením patričného archívu a stlačením zeleného tlačidla.

---


## Streamy ##
Pre zadefinovanie vlastných streamov je potrebné editovať súbor _streams.xml_ nachádzajúci sa v adresáry _streams_ v koreňovom adresáry pluginu

---

## Ovládanie ##

### Video prehrávač ###
  * **RADIO,REFRESH** - zobrazí aktuálne sťahované súbory
  * **5,ASPECT** - zmena pomeru strán
  * **TEXT,SUBTITLES** - nastavenie tituliek

### Archívy ###
  * **RADIO,REFRESH** - kdekoľvek v menu zobrazí aktuálne sťahované súbory
  * **5 - zobrazenie info o položke v CSFD plugine

---

## Sťahovanie ##
Sťahovať by sa malo dať akýkolvek archív je potrebné dostať sa až k videu, stlačiť menu, čím otvoríme kontextové menu videa:
  ***Prehrávať**- začne prehrávať bez sťahovania
  ***Prehrávať a sťahovať**- začne hneď sťahovať a prehrávať ho začne po stanovenej dobe v nastavení pluginu "Prehrávať po"
  ***Sťahovať**- začne sťahovať video**

### Stav sťahovania/í ###

Zobrazíme ho cez tlačidlo [radio](radio.md) alebo [refresh](refresh.md) v plugine.
  * **Prerušiť sťahovanie** - ukončí predčasne sťahovanie a nezmaže sťahovaný súbor
  * **Zmazať** - ak prebieha sťahovanie - preruší ho, vymaže sťahovaný súbor
  * **Prehrávať** - začne prehrávať aj nie komplentne stiahnutý súbor (Prehrávač sa môže správať nestabilne...)
  * **Zobraziť podrobnejšie informácie o sťahovaní** - prostredníctvom tlačidla **OK** je možné zobraziť stav sťahovania v percentách, ETA,.. sťahovaného súboru.

### Ďaľšie poznámky k sťahovaniu ###

  * sťahovanie pokračuje aj po vypnutí pluginu. O úspešnom či neúspešnom sťahovaní sme informovaný aj mimo pluginu informačnou správou

  * sťahovanie pokračuje aj po reštarte enigmy2, v tomto prípade sa ale vymaže zoznam sťahovaných súborov a nemáme informácie o priebehu sťahovaní(mám v pláne spraviť)

  * pri "prehrávaní a sťahovaní" avi súborov (movielibrary), je použité sťahovanie priamo späté so spustenou enigmou2, čiže po jej reštarte sa sťahovanie preruší.

  * je možné dať sťahovať viac súborov naraz, treba ale myslieť aj na to, že každé sťahovanie pridá nároky na procesor, čiže sa môže enigma2 viditeľne spomaliť.

  * niektoré servery neumožňujú sťahovať viac ako 1 súbor naraz - movielibrary.


---

## Poznámky k niektorým archívom ##

  * prehravanie youtube archivov(videacesky,nastojaka a pohadkar) na sh4(libeplayer3) nefunkcne, je potrebne najprv stiahnut/dat prehravat a stahovat..

  * voyo.cz - [heslo](http://code.google.com/p/dmd-xbmc/wiki/Heslo_V0Y0)

  * upozornenie/tip pre movielibrary - Ked dame stahovat a potom z menu prehravat, prehra sa len tolko kolko bolo dovtedy stiahnute. Ked dame prehravat a stahovat, bude sa prehravat tolko kolko je stiahnute, ak ale nebude stihat stahovat, tak sa zasekne enigma2, preto je lepsie hned ako sa da prehravat a stahovat v movielibrary vystupit z filmu a nechat pokracovat stahovanie. Nasledne ist do zoznamu stahovani(refresh) pozret stav, a ked uvazime za vhodne, ze je uz dostatok filmu stiahnuteho potom pustit aby sa e2 nezasekla, tyka sa to vacsich suborov~>1GB na priemerne dlhy film, kedze ulozto ide max 300KB/s. Pri by to malo ist ako ma. Uz robim fix len este neni dokonceny...
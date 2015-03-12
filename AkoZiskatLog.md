### Ak sa jedná o kritickú chybu (zelená obrazovka) a máte pripojený disk ###

Log je možné nájsť v priečinku _/media/hdd_ vo formáte _enigma2\_crash\_xxxxxxxxxx.log_, ak ich tam máte viac, pošlite ten posledne vytvorený.

### Ak sa nejedná o kritickú chybu, prípadne nemáte pripojený disk, log môžete vytvoriť nasledovne ###

Je potrebné pripojiť sa cez telnet k sat. príjmaču a zadať do konzoly nasledujúce príkazy:

  * **init 4** - vypne sa enigma2
  * **enigma2 2> /tmp/e2.log** - spustí sa enigma2 a log sa zapisuje do _/tmp/e2.log_
Teraz je potrebné dostať sa k problému/chybe. Akonáhle je tak učinené je možné enigmu2 vypnúť.
  * **killall enigma2** - vypne sa enigma2
  * **init 3** - enigma2 sa naštartuje v pôvodnom stave

Log je teda v _/tmp/e2.log_ súbore.
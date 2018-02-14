# Battleship Bot

## Informasi
Authors:  
Ayrton Cyril / 13516019  
Dionesius Agung Andika P / 13516043  
Dicky Adrian / 13516050


## Deskripsi Singkat
### Pendahuluan
Bot Battleship untuk Entellect Challenge 2017: Battleships ([link github](https://github.com/EntelectChallenge/2017-Battleships)).  
Dibuat untuk Tugas Besar I IF2211 - Strategi Algoritma tahun 2018, Program Studi Informatika, Institut Teknologi Bandung.  
Dibuat dalam bahasa Python 3 menggunakan Python 3 standard libraries.

### Isi Direktori dan Penjelasan
bot.py           : program bot yang akan dijalankan oleh game engine  
bot.json         : berisi metadata dari bot  
data.json        : berisi konfigurasi-konfigurasi dan data-data yang disimpan oleh bot selama game berlangsung  
requirements.txt : berisi informasi library-library tambahan yang diperlukan oleh bot saat game berlangsung

## Penggunaan

Di direktori tempat game engine berada, buka command prompt dan ketikkan
```
Battleships.exe --pretty -b "<path-ke-folder-opponent-bot>" "<path-ke-folder-bot-ini>" [-s 2]
```
untuk bermain melawan bot lain, atau
```
Battleships.exe --pretty -b "<path-ke-folder-bot-ini>" -c 1 [-s 2]
```
untuk human vs bot ini.
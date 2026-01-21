# Quick Start Guide

## Hapat e Shpejta për Fillim

### 1. Instalimi

```bash
pip install -r requirements.txt
```

### 2. Nisja e Sistemit

```bash
python main.py
```

### 3. Hapja e Dashboard

Shkoni te: http://127.0.0.1:5000

### 4. Vëzhgimi

- Sensorët do të lexojnë vlera çdo 1-3 sekonda
- Rregullat do të zbatohen automatikisht
- Dashboard-i do të përditësohet çdo 2 sekonda

### 5. Testimi i Rregullave

**Test 1: Ngrohja**
- Ndryshoni `temperature_threshold_low` në `config.json` në 25°C
- Vëzhgoni se ngrohja ndizet automatikisht

**Test 2: Dritat**
- Ndryshoni `light_threshold_low` në 80%
- Vëzhgoni se dritat ndizen kur ka lëvizje

**Test 3: Alarmi**
- Vendosni `home_occupied` në `false` në `config.json`
- Vëzhgoni alarmin kur detektohet lëvizje

### 6. Kontrolli Manual

Në dashboard, mund të kontrolloni manualisht:
- Dritat (toggle switch)
- Ngrohjen (toggle switch)
- Alarmin (toggle switch)

### 7. Log Files

Kontrolloni log files në: `logs/smart_home.log`

### 8. Ndalja

Shtypni `Ctrl+C` për të ndaluar sistemin në mënyrë të sigurt.

## Troubleshooting

**Problem**: Port 5000 është i zënë
**Zgjidhje**: Ndryshoni port në `config.json` → `flask.port`

**Problem**: Import errors
**Zgjidhje**: Sigurohuni që jeni në directory-in e projektit dhe që keni instaluar requirements

**Problem**: Dashboard nuk përditësohet
**Zgjidhje**: Kontrolloni console për errors, refresh browser

## Komanda të Dobishme

```bash
# Testimi
python test_basic.py

# Verifikimi i strukturës
python -c "from hub import SmartHub; print('OK')"
```



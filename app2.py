from flask import Flask, request, jsonify, send_from_directory
from config import *
from encrypt import *
import threading
import time
import socket
import json
import base64
import requests
from datetime import datetime
import jwt
from google.protobuf.timestamp_pb2 import Timestamp
import errno
import select
import atexit
import os
import signal
import sys
import psutil
import urllib3
import random
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
clients = {}
shutting_down = False

# ==================== Embedded VIP index.html ====================
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>NIROB GHOST — VIP TOOL</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
:root{
  --gold:#FFD700;--gold2:#FFA500;--dark:#02020A;
  --panel:rgba(255,215,0,0.045);--border:rgba(255,215,0,0.18);
  --glow:0 0 30px rgba(255,215,0,0.4);
  --red:#FF3B3B;--green:#00FF88;--blue:#00BFFF;--purple:#BF5FFF;
  --cyan:#00FFFF;--pink:#FF69B4;--lime:#ADFF2F;
}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{
  background:var(--dark);
  font-family:'Rajdhani',sans-serif;
  color:#e0e0e0;min-height:100vh;
  overflow-x:hidden;position:relative;
}

/* animated grid bg */
body::before{
  content:'';position:fixed;inset:0;
  background-image:
    linear-gradient(rgba(255,215,0,0.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,215,0,0.025) 1px,transparent 1px);
  background-size:44px 44px;
  pointer-events:none;z-index:0;
  animation:gridMove 20s linear infinite;
}
@keyframes gridMove{0%{background-position:0 0;}100%{background-position:44px 44px;}}

/* top glow */
body::after{
  content:'';position:fixed;
  top:-25%;left:50%;transform:translateX(-50%);
  width:1000px;height:700px;
  background:radial-gradient(ellipse,rgba(255,180,0,0.07) 0%,transparent 70%);
  pointer-events:none;z-index:0;
}

/* particles */
.particles{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.p{position:absolute;border-radius:50%;animation:pfloat linear infinite;opacity:0;}
@keyframes pfloat{
  0%{transform:translateY(100vh) scale(0);opacity:0;}
  10%{opacity:.5;}
  90%{opacity:.3;}
  100%{transform:translateY(-10vh) scale(1);opacity:0;}
}

.wrapper{position:relative;z-index:1;max-width:980px;margin:0 auto;padding:20px 12px 70px;}

/* ══ HEADER ══ */
.header-bar{
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(255,215,0,0.03);
  border:1px solid var(--border);border-radius:12px;
  padding:10px 18px;margin-bottom:18px;
  backdrop-filter:blur(10px);
}
.header-logo{font-family:'Orbitron',monospace;font-size:10px;color:rgba(255,215,0,.5);letter-spacing:3px;}
.header-status{display:flex;gap:8px;align-items:center;}
.h-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green);animation:pulseLive 1s ease-in-out infinite;}
.h-txt{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--green);letter-spacing:1px;}

/* ══ LOGO ══ */
.logo-wrap{text-align:center;padding:24px 0 8px;position:relative;}
.logo-ghost{
  display:inline-block;font-size:80px;
  animation:floatGhost 3s ease-in-out infinite;
  filter:drop-shadow(0 0 24px rgba(255,215,0,.9)) drop-shadow(0 0 50px rgba(255,150,0,.6));
  line-height:1;cursor:default;
}
@keyframes floatGhost{
  0%,100%{transform:translateY(0) rotate(-4deg) scale(1);}
  50%{transform:translateY(-18px) rotate(4deg) scale(1.05);}
}
.logo-title{
  font-family:'Orbitron',monospace;
  font-size:clamp(24px,5.5vw,42px);
  font-weight:900;letter-spacing:5px;
  background:linear-gradient(135deg,#FFD700 0%,#FF8C00 40%,#FFD700 70%,#FFF176 100%);
  background-size:300%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:shimmerText 2.5s linear infinite;
  margin:8px 0 4px;
  text-shadow:none;
}
@keyframes shimmerText{0%{background-position:0% 50%;}100%{background-position:300% 50%;}}
.logo-sub{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--gold2);letter-spacing:7px;opacity:.65;text-transform:uppercase;}
.badges-row{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:12px;}
.badge{
  display:inline-flex;align-items:center;gap:5px;
  border-radius:20px;padding:4px 14px;
  font-family:'Orbitron',monospace;font-size:9px;letter-spacing:2px;
}
.badge-live{background:rgba(255,50,50,.15);border:1px solid rgba(255,50,50,.45);color:#FF6B6B;}
.badge-vip{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.45);color:var(--gold);}
.badge-inf{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.4);color:var(--green);}
.live-dot{width:7px;height:7px;border-radius:50%;background:#FF3B3B;animation:pulseLive 1s ease-in-out infinite;box-shadow:0 0 8px #FF3B3B;}
@keyframes pulseLive{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.35;transform:scale(.65);}}

/* ══ STATS ══ */
.stats-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:22px 0 16px;}
.stat-card{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:12px;
  padding:16px 10px 12px;
  text-align:center;
  position:relative;overflow:hidden;
  transition:transform .25s,border-color .25s,box-shadow .25s;
  cursor:default;
}
.stat-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent);
  animation:scanLine 3s linear infinite;
}
@keyframes scanLine{0%{transform:translateX(-100%);}100%{transform:translateX(100%);}}
.stat-card:hover{transform:translateY(-4px);border-color:var(--gold);box-shadow:var(--glow);}
.stat-icon{font-size:22px;margin-bottom:4px;}
.stat-value{
  font-family:'Orbitron',monospace;font-size:19px;font-weight:700;
  color:var(--gold);text-shadow:0 0 12px rgba(255,215,0,.6);
}
.stat-label{font-size:9px;color:rgba(255,215,0,.45);letter-spacing:2px;text-transform:uppercase;margin-top:3px;}

/* ══ REFRESH ══ */
.refresh-bar-wrap{
  background:rgba(255,215,0,.03);border:1px solid var(--border);
  border-radius:10px;padding:10px 15px;margin-bottom:14px;
  display:flex;align-items:center;gap:12px;flex-wrap:wrap;
}
.refresh-bar-label{font-family:'Share Tech Mono',monospace;font-size:10px;color:rgba(255,215,0,.55);letter-spacing:1px;white-space:nowrap;}
.refresh-progress{flex:1;height:3px;background:rgba(255,215,0,.1);border-radius:2px;overflow:hidden;min-width:60px;}
.refresh-fill{height:100%;background:linear-gradient(90deg,var(--gold),var(--gold2));border-radius:2px;width:100%;transition:width 1s linear;box-shadow:0 0 8px rgba(255,215,0,.5);}
.refresh-countdown{font-family:'Orbitron',monospace;font-size:11px;color:var(--gold);min-width:26px;text-align:right;}
.refresh-toggle{background:transparent;border:1px solid var(--border);border-radius:6px;color:rgba(255,215,0,.55);font-family:'Share Tech Mono',monospace;font-size:10px;padding:4px 10px;cursor:pointer;transition:all .2s;letter-spacing:1px;}
.refresh-toggle:hover,.refresh-toggle.on{background:rgba(255,215,0,.1);color:var(--gold);border-color:var(--gold);}

/* ══ TABS ══ */
.tabs{display:flex;gap:3px;background:rgba(255,215,0,.025);border:1px solid var(--border);border-radius:12px;padding:4px;margin-bottom:16px;flex-wrap:wrap;}
.tab-btn{
  flex:1;min-width:65px;padding:10px 5px;
  border:none;border-radius:8px;background:transparent;
  color:rgba(255,215,0,.35);
  font-family:'Orbitron',monospace;font-size:9px;font-weight:600;
  letter-spacing:.5px;cursor:pointer;transition:all .25s;text-transform:uppercase;
  position:relative;overflow:hidden;
}
.tab-btn.active{
  background:linear-gradient(135deg,rgba(255,215,0,.18),rgba(255,140,0,.12));
  color:var(--gold);
  box-shadow:inset 0 0 20px rgba(255,215,0,.1),0 0 18px rgba(255,215,0,.18);
}
.tab-btn::after{content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:0;height:2px;background:var(--gold);border-radius:1px;transition:width .25s;}
.tab-btn.active::after{width:60%;}

/* ══ PANELS ══ */
.panel{display:none;animation:panelIn .3s ease;}
.panel.active{display:block;}
@keyframes panelIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

/* ══ CARD ══ */
.card{
  background:var(--panel);
  border:1px solid var(--border);
  border-radius:16px;
  padding:22px;margin-bottom:14px;
  position:relative;overflow:hidden;
  backdrop-filter:blur(6px);
  transition:border-color .3s;
}
.card:hover{border-color:rgba(255,215,0,.28);}
.card::after{
  content:'';position:absolute;
  top:0;right:0;
  width:120px;height:120px;
  background:radial-gradient(ellipse,rgba(255,215,0,.04) 0%,transparent 70%);
  pointer-events:none;
}
.card-title{
  font-family:'Orbitron',monospace;font-size:12px;
  color:var(--gold);letter-spacing:3px;text-transform:uppercase;
  margin-bottom:18px;display:flex;align-items:center;gap:10px;
}
.card-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(255,215,0,.4),transparent);}

/* ══ FORM ══ */
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.form-group{margin-bottom:14px;}
.form-label{display:block;font-family:'Share Tech Mono',monospace;font-size:10px;color:rgba(255,215,0,.6);letter-spacing:2px;text-transform:uppercase;margin-bottom:7px;}
.form-input{
  width:100%;padding:13px 16px;
  background:rgba(0,0,0,.55);
  border:1px solid rgba(255,215,0,.18);
  border-radius:9px;color:#fff;
  font-family:'Share Tech Mono',monospace;font-size:14px;
  outline:none;transition:border-color .2s,box-shadow .2s,background .2s;
}
.form-input:focus{border-color:var(--gold);box-shadow:0 0 18px rgba(255,215,0,.22);background:rgba(0,0,0,.7);}
.form-input::placeholder{color:rgba(255,255,255,.18);}

/* ══ BUTTONS ══ */
.btn{
  width:100%;padding:14px;border:none;border-radius:11px;
  font-family:'Orbitron',monospace;font-size:12px;font-weight:700;
  letter-spacing:2px;text-transform:uppercase;
  cursor:pointer;position:relative;overflow:hidden;
  transition:all .25s;
}
.btn-primary{background:linear-gradient(135deg,#FFD700,#FF8C00);color:#000;box-shadow:0 4px 22px rgba(255,165,0,.4);}
.btn-primary:hover:not(:disabled){transform:translateY(-3px);box-shadow:0 10px 32px rgba(255,165,0,.55);}
.btn-danger{background:linear-gradient(135deg,#FF3B3B,#CC0000);color:#fff;box-shadow:0 4px 22px rgba(255,50,50,.3);}
.btn-danger:hover:not(:disabled){transform:translateY(-3px);box-shadow:0 10px 32px rgba(255,50,50,.45);}
.btn-purple{background:linear-gradient(135deg,#7B2FFF,#BF5FFF);color:#fff;box-shadow:0 4px 22px rgba(130,50,255,.4);}
.btn-purple:hover:not(:disabled){transform:translateY(-3px);box-shadow:0 10px 32px rgba(130,50,255,.55);}
.btn::before{content:'';position:absolute;top:-50%;left:-70%;width:40%;height:200%;background:rgba(255,255,255,.18);transform:skewX(-20deg);transition:left .45s;}
.btn:hover::before{left:130%;}
.btn:active:not(:disabled){transform:translateY(0)!important;}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none!important;}

/* ══ SPINNER ══ */
.spin{display:inline-block;width:14px;height:14px;border:2px solid rgba(0,0,0,.25);border-top-color:#000;border-radius:50%;animation:spin .55s linear infinite;vertical-align:middle;margin-right:7px;}
.spin-w{border-color:rgba(255,255,255,.25);border-top-color:#fff;}
@keyframes spin{to{transform:rotate(360deg);}}

/* ══ RESULT BOX ══ */
.result-box{
  margin-top:14px;padding:14px;border-radius:10px;
  font-family:'Share Tech Mono',monospace;font-size:11px;line-height:1.8;
  display:none;animation:fadeSlide .3s ease;white-space:pre-wrap;word-break:break-all;
}
@keyframes fadeSlide{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
.result-box.success{display:block;background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.35);color:var(--green);}
.result-box.error{display:block;background:rgba(255,59,59,.07);border:1px solid rgba(255,59,59,.35);color:var(--red);}
.result-box.info{display:block;background:rgba(0,191,255,.07);border:1px solid rgba(0,191,255,.35);color:var(--blue);}

/* ══ GHOST SELECT LIST ══ */
.ghost-select-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:10px 0 16px;}
.ghost-select-item{
  background:rgba(130,50,255,.08);
  border:1px solid rgba(130,50,255,.25);
  border-radius:9px;padding:9px 12px;
  display:flex;align-items:center;gap:8px;
  cursor:pointer;transition:all .2s;
  font-family:'Share Tech Mono',monospace;font-size:11px;
}
.ghost-select-item:hover{border-color:rgba(191,95,255,.55);background:rgba(130,50,255,.15);}
.ghost-select-item input[type=checkbox]{accent-color:var(--gold);width:14px;height:14px;cursor:pointer;}
.ghost-select-item.selected{border-color:var(--gold);background:rgba(255,215,0,.08);}

.select-all-bar{
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(130,50,255,.06);border:1px solid rgba(130,50,255,.28);
  border-radius:10px;padding:11px 15px;margin-bottom:12px;gap:10px;
}
.select-all-label{font-family:'Share Tech Mono',monospace;font-size:11px;color:rgba(191,95,255,.9);letter-spacing:1px;}
.select-all-btn{
  background:linear-gradient(135deg,rgba(130,50,255,.2),rgba(191,95,255,.15));
  border:1px solid rgba(130,50,255,.5);border-radius:7px;
  color:#BF5FFF;font-family:'Share Tech Mono',monospace;font-size:10px;
  padding:6px 15px;cursor:pointer;transition:all .2s;letter-spacing:1px;
}
.select-all-btn:hover,.select-all-btn.on{background:linear-gradient(135deg,rgba(130,50,255,.4),rgba(191,95,255,.28));color:#fff;border-color:#BF5FFF;}

/* ══ CLIENTS ══ */
.clients-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:9px;margin-top:10px;}
.client-chip{
  background:rgba(0,0,0,.45);
  border:1px solid rgba(0,255,136,.22);
  border-radius:10px;padding:11px 13px;
  display:flex;flex-direction:column;gap:4px;
  position:relative;overflow:hidden;
  transition:all .2s;
}
.client-chip:hover{border-color:rgba(0,255,136,.5);transform:translateY(-2px);}
.client-chip::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,255,136,.4),transparent);}
.client-uid-row{display:flex;align-items:center;gap:6px;}
.client-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.dot-online{background:var(--green);box-shadow:0 0 7px var(--green);animation:pulseLive 1.5s ease-in-out infinite;}
.dot-offline{background:var(--red);box-shadow:0 0 7px var(--red);animation:none;}
.client-uid{font-family:'Orbitron',monospace;font-size:10px;font-weight:700;}
.client-meta{font-family:'Share Tech Mono',monospace;font-size:9px;color:rgba(255,255,255,.3);}
.client-mins{
  display:inline-block;background:rgba(255,165,0,.12);
  border:1px solid rgba(255,165,0,.3);border-radius:4px;
  padding:1px 6px;font-family:'Orbitron',monospace;font-size:8px;color:var(--gold2);
  margin-top:2px;
}
.tag-on{background:rgba(0,255,136,.14);border:1px solid rgba(0,255,136,.4);border-radius:4px;padding:1px 6px;font-family:'Orbitron',monospace;font-size:8px;color:var(--green);}
.tag-off{background:rgba(255,59,59,.12);border:1px solid rgba(255,59,59,.35);border-radius:4px;padding:1px 6px;font-family:'Orbitron',monospace;font-size:8px;color:var(--red);}
.no-clients{color:rgba(255,255,255,.28);font-family:'Share Tech Mono',monospace;font-size:12px;text-align:center;padding:28px;}

/* ══ ACCOUNTS TABLE ══ */
.acc-table{width:100%;border-collapse:collapse;font-family:'Share Tech Mono',monospace;font-size:11px;margin-top:10px;}
.acc-table th{color:rgba(255,215,0,.55);letter-spacing:2px;text-align:left;padding:9px 10px;border-bottom:1px solid var(--border);font-size:9px;}
.acc-table td{padding:9px 10px;border-bottom:1px solid rgba(255,215,0,.05);vertical-align:middle;}
.acc-table tr:hover td{background:rgba(255,215,0,.025);}

/* ══ LOG ══ */
.log-box{
  background:rgba(0,0,0,.65);border:1px solid rgba(255,215,0,.1);
  border-radius:10px;height:220px;overflow-y:auto;
  padding:12px;font-family:'Share Tech Mono',monospace;font-size:11px;line-height:1.75;
  margin-top:8px;
}
.log-box::-webkit-scrollbar{width:3px;}
.log-box::-webkit-scrollbar-track{background:transparent;}
.log-box::-webkit-scrollbar-thumb{background:rgba(255,215,0,.2);border-radius:2px;}
.log-row{display:flex;gap:8px;align-items:flex-start;}
.log-t{color:rgba(255,215,0,.35);white-space:nowrap;flex-shrink:0;}
.log-m.ok{color:var(--green);}
.log-m.fail{color:var(--red);}
.log-m.info{color:var(--blue);}
.log-m.warn{color:var(--gold2);}

/* ══ TOAST ══ */
.toast{
  position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(24px);
  background:rgba(0,0,0,.96);border:1px solid var(--gold);
  border-radius:10px;padding:10px 24px;
  font-family:'Orbitron',monospace;font-size:10px;color:var(--gold);letter-spacing:2px;
  z-index:9999;opacity:0;transition:all .3s;pointer-events:none;white-space:nowrap;
  box-shadow:0 0 20px rgba(255,215,0,.3);
}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0);}

/* ══ MINUTE DISPLAY ══ */
.big-mins{
  font-family:'Orbitron',monospace;font-size:clamp(28px,6vw,52px);font-weight:900;
  color:var(--gold);text-shadow:0 0 20px rgba(255,215,0,.6),0 0 40px rgba(255,150,0,.3);
  text-align:center;padding:16px 0 6px;letter-spacing:3px;
  animation:pulseNum 2s ease-in-out infinite;
}
@keyframes pulseNum{0%,100%{text-shadow:0 0 20px rgba(255,215,0,.6),0 0 40px rgba(255,150,0,.3);}50%{text-shadow:0 0 30px rgba(255,215,0,.9),0 0 60px rgba(255,150,0,.5),0 0 80px rgba(255,215,0,.2);}}
.mins-label{text-align:center;font-family:'Share Tech Mono',monospace;font-size:10px;color:rgba(255,215,0,.5);letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;}

/* ══ DIVIDER ══ */
.divider{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:16px 0;}

/* ══ FOOTER ══ */
.footer{text-align:center;padding-top:26px;font-family:'Share Tech Mono',monospace;font-size:10px;color:rgba(255,215,0,.2);letter-spacing:3px;text-transform:uppercase;}
.watermark{position:fixed;bottom:10px;right:14px;font-family:'Orbitron',monospace;font-size:8px;color:rgba(255,215,0,.12);letter-spacing:2px;z-index:10;}
.corner-tl,.corner-br{position:fixed;width:65px;height:65px;pointer-events:none;z-index:0;opacity:.12;}
.corner-tl{top:0;left:0;border-top:2px solid var(--gold);border-left:2px solid var(--gold);}
.corner-br{bottom:0;right:0;border-bottom:2px solid var(--gold);border-right:2px solid var(--gold);}

/* ══ COLOR PALETTE ══ */
.c0{color:#FF6B6B;} .c1{color:#FFD700;} .c2{color:#00FF88;} .c3{color:#00BFFF;}
.c4{color:#BF5FFF;} .c5{color:#FF8C00;} .c6{color:#FF69B4;} .c7{color:#00FFFF;}
.c8{color:#ADFF2F;} .c9{color:#FF4500;} .c10{color:#F0E68C;} .c11{color:#7FFFD4;}

/* ══ RESPONSIVE ══ */
@media(max-width:580px){
  .stats-bar{grid-template-columns:repeat(2,1fr);}
  .form-row{grid-template-columns:1fr;}
  .tab-btn{font-size:8px;padding:8px 3px;}
  .logo-ghost{font-size:60px;}
  .big-mins{font-size:32px;}
}
</style>
</head>
<body>

<!-- Particles -->
<div class="particles" id="particles"></div>
<div class="corner-tl"></div>
<div class="corner-br"></div>
<div class="toast" id="toast"></div>

<div class="wrapper">

  <!-- HEADER BAR -->
  <div class="header-bar">
    <span class="header-logo">NIROB GHOST v4.0 VIP</span>
    <div class="header-status">
      <span class="h-dot"></span>
      <span class="h-txt" id="hStatus">SERVER ONLINE</span>
    </div>
  </div>

  <!-- LOGO -->
  <div class="logo-wrap">
    <div class="logo-ghost">👻</div>
    <div class="logo-title">NIROB GHOST</div>
    <div class="logo-sub">VIP Ghost Tool &nbsp;|&nbsp; Free Fire TCP</div>
    <div class="badges-row">
      <div class="badge badge-live"><span class="live-dot"></span>LIVE</div>
      <div class="badge badge-vip">⚡ VIP TOOL</div>
      <div class="badge badge-inf">∞ INFINITE MATCH</div>
    </div>
  </div>

  <!-- BIG MINUTES DISPLAY -->
  <div class="card" style="margin-top:18px;text-align:center;">
    <div class="card-title" style="justify-content:center;">⏱ MATCH DURATION</div>
    <div class="mins-label">TOTAL MINUTES ACTIVE</div>
    <div class="big-mins" id="bigMins">0</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:rgba(255,215,0,.4);text-align:center;padding-bottom:6px;" id="bigMinsFormatted">Starting...</div>
  </div>

  <!-- STATS -->
  <div class="stats-bar">
    <div class="stat-card">
      <div class="stat-icon">🌐</div>
      <div class="stat-value" id="statClients">0</div>
      <div class="stat-label">Clients</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">✅</div>
      <div class="stat-value" id="statSent">0</div>
      <div class="stat-label">Sent</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">💀</div>
      <div class="stat-value" id="statGhosts">0</div>
      <div class="stat-label">Ghosts</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">⏱</div>
      <div class="stat-value" id="statUptime">00:00</div>
      <div class="stat-label">Uptime</div>
    </div>
  </div>

  <!-- AUTO REFRESH -->
  <div class="refresh-bar-wrap">
    <span class="refresh-bar-label">AUTO REFRESH</span>
    <div class="refresh-progress"><div class="refresh-fill" id="rFill"></div></div>
    <span class="refresh-countdown" id="rCount">7s</span>
    <button class="refresh-toggle on" id="rToggle" onclick="toggleRefresh()">ON</button>
  </div>

  <!-- TABS -->
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('ghost',this)">👻 GHOST</button>
    <button class="tab-btn" onclick="switchTab('ghostall',this)">👥 ALL</button>
    <button class="tab-btn" onclick="switchTab('adduid',this)">➕ ADD UID</button>
    <button class="tab-btn" onclick="switchTab('clients',this)">🔌 CLIENTS</button>
    <button class="tab-btn" onclick="switchTab('logs',this)">📋 LOGS</button>
  </div>

  <!-- ══ GHOST PANEL ══ -->
  <div class="panel active" id="panel-ghost">
    <div class="card">
      <div class="card-title">👻 Single Ghost</div>
      <div class="form-group">
        <label class="form-label">Team Code</label>
        <input class="form-input" id="g-tc" type="text" placeholder="Enter team code (1-7 digits)" maxlength="7">
      </div>
      <div class="form-group">
        <label class="form-label">Ghost Name</label>
        <input class="form-input" id="g-name" type="text" placeholder="Enter ghost display name">
      </div>
      <button class="btn btn-primary" id="g-btn" onclick="sendGhost()">👻 SEND GHOST</button>
      <div class="result-box" id="g-res"></div>
    </div>
    <!-- minute info -->
    <div class="card">
      <div class="card-title">⏱ Ghost Duration Info</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:rgba(255,255,255,.6);line-height:2;">
        Ghost stays in match for: <span style="color:var(--gold);font-family:'Orbitron',monospace;">22,365,447 minutes</span><br>
        = <span style="color:var(--green);">42 years, 5 months, 3 days</span><br>
        = <span style="color:var(--blue);">Practically FOREVER ∞</span>
      </div>
    </div>
  </div>

  <!-- ══ GHOST ALL PANEL ══ -->
  <div class="panel" id="panel-ghostall">
    <div class="card">
      <div class="card-title">👥 Ghost All Clients</div>

      <div class="select-all-bar">
        <span class="select-all-label">👥 GHOST SELECTION</span>
        <button class="select-all-btn on" id="selAllBtn" onclick="toggleSelectAll()">☑ ALL SELECTED</button>
      </div>

      <div class="ghost-select-grid" id="ghostSelGrid">
        <div class="no-clients">Load clients first...</div>
      </div>

      <div class="divider"></div>

      <div class="form-group">
        <label class="form-label">Team Code</label>
        <input class="form-input" id="ga-tc" type="text" placeholder="Enter team code" maxlength="7">
      </div>
      <div class="form-group">
        <label class="form-label">Ghost Names <span style="opacity:.45;font-size:9px;">(comma separated  or  {name1}{name2})</span></label>
        <input class="form-input" id="ga-names" type="text" placeholder="Ghost1, Ghost2, Ghost3">
      </div>
      <button class="btn btn-purple" id="ga-btn" onclick="sendGhostAll()">👥 SEND GHOST ALL</button>
      <div class="result-box" id="ga-res"></div>
    </div>
  </div>

  <!-- ══ ADD UID PANEL ══ -->
  <div class="panel" id="panel-adduid">
    <div class="card">
      <div class="card-title">➕ Add Guest UID</div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Guest UID</label>
          <input class="form-input" id="c-uid" type="text" placeholder="Enter UID">
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input class="form-input" id="c-pass" type="password" placeholder="Enter password">
        </div>
      </div>
      <button class="btn btn-primary" id="c-add-btn" onclick="addClient()">➕ ADD & CONNECT NOW</button>
      <div class="result-box" id="c-res"></div>
    </div>
    <div class="card">
      <div class="card-title">📋 Saved in accounts.json</div>
      <div id="savedAccWrap"><div class="no-clients">⏳ Loading...</div></div>
      <div class="divider"></div>
      <div class="form-group" style="margin-bottom:0;">
        <label class="form-label">Remove UID</label>
        <div style="display:flex;gap:8px;">
          <input class="form-input" id="c-rm-id" type="text" placeholder="UID to remove" style="flex:1;">
          <button onclick="removeClient()" style="padding:0 18px;border:none;border-radius:9px;background:linear-gradient(135deg,#FF3B3B,#CC0000);color:#fff;font-family:'Orbitron',monospace;font-size:10px;cursor:pointer;letter-spacing:1px;white-space:nowrap;">REMOVE</button>
        </div>
        <div class="result-box" id="c-rm-res" style="margin-top:10px;"></div>
      </div>
    </div>
  </div>

  <!-- ══ CLIENTS PANEL ══ -->
  <div class="panel" id="panel-clients">
    <div class="card">
      <div class="card-title">🔌 Connected Clients</div>
      <div id="clients-list"><div class="no-clients">⏳ Loading clients...</div></div>
    </div>
  </div>

  <!-- ══ LOGS PANEL ══ -->
  <div class="panel" id="panel-logs">
    <div class="card">
      <div class="card-title">📋 Activity Log</div>
      <div style="display:flex;justify-content:flex-end;margin-bottom:8px;">
        <button onclick="clearLogs()" style="background:rgba(255,50,50,.1);border:1px solid rgba(255,50,50,.3);color:#FF6B6B;font-family:'Share Tech Mono',monospace;font-size:9px;padding:4px 12px;border-radius:6px;cursor:pointer;letter-spacing:1px;">CLEAR LOGS</button>
      </div>
      <div class="log-box" id="logBox"></div>
    </div>
  </div>

  <div class="footer">NIROB GHOST VIP TOOL &nbsp;●&nbsp; Developer @NIROB_353 &nbsp;●&nbsp; FF TCP</div>
</div>
<div class="watermark">NIROB GHOST v4.0 VIP</div>

<script>
// ═══════════════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════════════
const GHOST_MINS  = 22365447;
const COLORS      = ['c0','c1','c2','c3','c4','c5','c6','c7','c8','c9','c10','c11'];
const REFRESH_INT = 7;
const START_TIME  = Date.now();

let totalSent   = 0;
let totalGhosts = 0;
let refreshOn   = true;
let refreshSecs = REFRESH_INT;
let rTimer, cdTimer;
let clientList  = [];
let clientDetails = [];
let minuteTimer = null;
let elapsedMins = 0;

// ═══════════════════════════════════════════════
// PARTICLES
// ═══════════════════════════════════════════════
(function spawnParticles(){
  const box=document.getElementById('particles');
  for(let i=0;i<22;i++){
    const p=document.createElement('div');
    p.className='p';
    const sz=Math.random()*4+1;
    p.style.cssText=`
      width:${sz}px;height:${sz}px;
      left:${Math.random()*100}%;
      background:rgba(255,${Math.floor(Math.random()*100+150)},0,0.6);
      animation-duration:${Math.random()*12+8}s;
      animation-delay:${Math.random()*10}s;
      box-shadow:0 0 ${sz*2}px rgba(255,215,0,.5);
    `;
    box.appendChild(p);
  }
})();

// ═══════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════
function nowStr(){return new Date().toTimeString().slice(0,8);}

function toast(msg,clr='var(--gold)'){
  const t=document.getElementById('toast');
  t.textContent=msg;
  t.style.color=clr;
  t.style.borderColor=clr;
  t.style.boxShadow=`0 0 20px ${clr}40`;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),2800);
}

function addLog(msg,type='info'){
  const box=document.getElementById('logBox');
  const row=document.createElement('div');
  row.className='log-row';
  row.innerHTML=`<span class="log-t">[${nowStr()}]</span><span class="log-m ${type}">${msg}</span>`;
  box.appendChild(row);
  box.scrollTop=box.scrollHeight;
  while(box.children.length>400)box.removeChild(box.firstChild);
}

function clearLogs(){document.getElementById('logBox').innerHTML='';}

function showRes(id,msg,type){
  const el=document.getElementById(id);
  if(!el)return;
  el.className='result-box '+type;
  el.textContent=msg;
}

function setBtn(id,loading,txt,cls='btn-primary'){
  const b=document.getElementById(id);
  if(!b)return;
  b.disabled=loading;
  const spinCls=cls==='btn-primary'?'spin':'spin spin-w';
  b.innerHTML=loading?`<span class="${spinCls}"></span>SENDING...`:txt;
}

// ═══════════════════════════════════════════════
// BIG MINUTES COUNTER
// ═══════════════════════════════════════════════
function formatBigMins(m){
  const mi=Math.floor(m);
  if(mi>=1440){
    const days=Math.floor(mi/1440);
    const hrs=Math.floor((mi%1440)/60);
    const mn=mi%60;
    return `${days.toLocaleString()} দিন, ${hrs} ঘন্টা, ${mn} মিনিট`;
  }
  if(mi>=60){
    const h=Math.floor(mi/60);const mn=mi%60;
    return `${h} ঘন্টা, ${mn} মিনিট`;
  }
  return `${mi} মিনিট`;
}

function startMinuteCounter(){
  clearInterval(minuteTimer);
  minuteTimer=setInterval(()=>{
    elapsedMins++;
    const display=elapsedMins>=1000000
      ? elapsedMins.toLocaleString()+'+ MINS'
      : elapsedMins.toLocaleString();
    document.getElementById('bigMins').textContent=display;
    document.getElementById('bigMinsFormatted').textContent=formatBigMins(elapsedMins);
  },60000); // every minute

  // also show seconds-based fake for impressive display
  let fakeMs=0;
  setInterval(()=>{
    fakeMs+=1;
    const shown=Math.floor(fakeMs/60)*1000 + fakeMs;
    if(fakeMs<60){
      document.getElementById('bigMins').textContent=fakeMs+' sec';
    }
  },1000);
}

// ═══════════════════════════════════════════════
// UPTIME
// ═══════════════════════════════════════════════
function updateUptime(){
  const s=Math.floor((Date.now()-START_TIME)/1000);
  const m=Math.floor(s/60),sec=s%60;
  document.getElementById('statUptime').textContent=
    String(m).padStart(2,'0')+':'+String(sec).padStart(2,'0');
  // update big mins with real seconds shown nicely
  const totalS=s;
  const mins=Math.floor(totalS/60);
  const secs=totalS%60;
  let minsStr='';
  if(mins>=1000000) minsStr=mins.toLocaleString()+' মিনিট';
  else if(mins>=1000) minsStr=mins.toLocaleString()+' মিনিট';
  else minsStr=mins+' মিনিট '+secs+' সেকেন্ড';
  document.getElementById('bigMins').textContent=totalS>=60?mins.toLocaleString():secs+'s';
  document.getElementById('bigMinsFormatted').textContent=
    totalS>=60?formatBigMins(mins):'Starting...';
}

// ═══════════════════════════════════════════════
// FETCH CLIENTS
// ═══════════════════════════════════════════════
async function fetchClients(){
  try{
    const r=await fetch('/list_clients');
    const d=await r.json();
    clientList=d.clients||[];
    clientDetails=d.client_details||[];
    document.getElementById('statClients').textContent=clientList.length;

    // Clients panel
    const wrap=document.getElementById('clients-list');
    if(clientList.length===0){
      wrap.innerHTML='<div class="no-clients">No clients connected</div>';
    } else {
      let html='<div class="clients-grid">';
      clientList.forEach((uid,i)=>{
        const cc=COLORS[i%COLORS.length];
        const det=clientDetails.find(x=>x.uid==uid)||{};
        const on=det.running!==false;
        const ts=det.connected_at?det.connected_at.slice(11,19):'--:--:--';
        html+=`<div class="client-chip">
          <div class="client-uid-row">
            <span class="client-dot ${on?'dot-online':'dot-offline'}"></span>
            <span class="client-uid ${cc}">${uid}</span>
            <span class="${on?'tag-on':'tag-off'}" style="margin-left:auto;">${on?'ON':'OFF'}</span>
          </div>
          <div class="client-meta">Since ${ts}</div>
          <div class="client-mins">∞ ${GHOST_MINS.toLocaleString()} mins</div>
        </div>`;
      });
      html+='</div>';
      wrap.innerHTML=html;
    }

    // Also refresh ghost select grid if that tab visible
    renderGhostSelGrid();
    return clientList;
  }catch(e){
    document.getElementById('clients-list').innerHTML=
      '<div class="no-clients">⚠ Failed to load clients</div>';
    return [];
  }
}

// ═══════════════════════════════════════════════
// GHOST SELECT GRID
// ═══════════════════════════════════════════════
function renderGhostSelGrid(){
  const wrap=document.getElementById('ghostSelGrid');
  if(!wrap)return;
  if(clientList.length===0){
    wrap.innerHTML='<div class="no-clients">No clients. Add UIDs first.</div>';
    return;
  }
  let html='';
  clientList.forEach((uid,i)=>{
    const cc=COLORS[i%COLORS.length];
    html+=`<label class="ghost-select-item selected" id="gsi-${uid}">
      <input type="checkbox" id="gs-${uid}" checked onchange="updateSelectItem('${uid}')">
      <span class="${cc}" style="font-weight:bold;font-family:'Orbitron',monospace;font-size:10px;">${uid}</span>
    </label>`;
  });
  wrap.innerHTML=html;
}

function updateSelectItem(uid){
  const cb=document.getElementById('gs-'+uid);
  const item=document.getElementById('gsi-'+uid);
  if(item)item.classList.toggle('selected',cb&&cb.checked);
}

let selAll=true;
function toggleSelectAll(){
  selAll=!selAll;
  const btn=document.getElementById('selAllBtn');
  btn.textContent=selAll?'☑ ALL SELECTED':'☐ DESELECT ALL';
  btn.classList.toggle('on',selAll);
  clientList.forEach(uid=>{
    const cb=document.getElementById('gs-'+uid);
    const item=document.getElementById('gsi-'+uid);
    if(cb){cb.checked=selAll;}
    if(item)item.classList.toggle('selected',selAll);
  });
}

// ═══════════════════════════════════════════════
// LOAD SAVED ACCOUNTS
// ═══════════════════════════════════════════════
async function loadSavedAccs(){
  const wrap=document.getElementById('savedAccWrap');
  if(!wrap)return;
  try{
    const r=await fetch('/list_clients');
    const d=await r.json();
    const list=d.clients||[];
    if(list.length===0){
      wrap.innerHTML='<div class="no-clients">No saved accounts.</div>';
      return;
    }
    let html='<table class="acc-table"><thead><tr><th>#</th><th>UID</th><th>STATUS</th><th>MINS</th></tr></thead><tbody>';
    list.forEach((uid,i)=>{
      const cc=COLORS[i%COLORS.length];
      html+=`<tr>
        <td style="color:rgba(255,215,0,.4);">${i+1}</td>
        <td class="${cc}" style="font-family:'Orbitron',monospace;font-weight:bold;font-size:10px;">${uid}</td>
        <td><span class="tag-on">ONLINE</span></td>
        <td><span class="client-mins">∞ ${(22365447).toLocaleString()}</span></td>
      </tr>`;
    });
    html+='</tbody></table>';
    wrap.innerHTML=html;
  }catch(e){
    wrap.innerHTML='<div class="no-clients">⚠ Could not load</div>';
  }
}

// ═══════════════════════════════════════════════
// AUTO REFRESH
// ═══════════════════════════════════════════════
function startRefresh(){
  refreshSecs=REFRESH_INT;
  updateCountdown();
  clearInterval(rTimer);
  rTimer=setInterval(()=>{
    if(!refreshOn)return;
    fetchClients();
    addLog('Auto-refreshed','info');
    refreshSecs=REFRESH_INT;
  },REFRESH_INT*1000);
  clearInterval(cdTimer);
  cdTimer=setInterval(()=>{
    if(!refreshOn)return;
    refreshSecs--;
    if(refreshSecs<0)refreshSecs=REFRESH_INT;
    updateCountdown();
  },1000);
}
function updateCountdown(){
  document.getElementById('rCount').textContent=refreshSecs+'s';
  document.getElementById('rFill').style.width=((refreshSecs/REFRESH_INT)*100)+'%';
}
function toggleRefresh(){
  refreshOn=!refreshOn;
  const b=document.getElementById('rToggle');
  b.textContent=refreshOn?'ON':'OFF';
  b.classList.toggle('on',refreshOn);
  addLog('Auto-refresh '+(refreshOn?'ON':'OFF'),'info');
}

// ═══════════════════════════════════════════════
// TAB SWITCH
// ═══════════════════════════════════════════════
function switchTab(name,btn){
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  if(btn)btn.classList.add('active');
  if(name==='ghostall'){fetchClients().then(()=>renderGhostSelGrid());}
  if(name==='adduid'){loadSavedAccs();}
  if(name==='clients'){fetchClients();}
}

// ═══════════════════════════════════════════════
// SEND GHOST (single)
// ═══════════════════════════════════════════════
async function sendGhost(){
  const tc=document.getElementById('g-tc').value.trim();
  const name=document.getElementById('g-name').value.trim()||'Ghost';
  if(!tc){showRes('g-res','⚠ Team code দিন!','error');return;}
  setBtn('g-btn',true,'','btn-primary');
  addLog(`Ghost → TC:${tc} NAME:${name}`,'info');
  try{
    const r=await fetch(`/ghost?teamcode=${encodeURIComponent(tc)}&ghost_name=${encodeURIComponent(name)}`);
    const d=await r.json();
    if(d.error){
      showRes('g-res','❌ '+d.error,'error');
      addLog('FAIL: '+d.error,'fail');
      toast('❌ Failed!','var(--red)');
    } else {
      const minsStr=(22365447).toLocaleString();
      showRes('g-res',`✅ SUCCESS!\n${d.result||JSON.stringify(d,null,2)}\n\n⏱ Duration: ${minsStr} minutes (∞ Forever)`,'success');
      totalSent++;totalGhosts++;
      document.getElementById('statSent').textContent=totalSent;
      document.getElementById('statGhosts').textContent=totalGhosts;
      addLog('OK → Ghost sent: '+name,'ok');
      toast('👻 Ghost sent!','var(--green)');
    }
  }catch(e){
    showRes('g-res','⚠ Network error: '+e.message,'error');
    addLog('Network error: '+e.message,'fail');
    toast('⚠ Network error','var(--gold2)');
  }
  setBtn('g-btn',false,'👻 SEND GHOST');
}

// ═══════════════════════════════════════════════
// GHOST ALL
// ═══════════════════════════════════════════════
async function sendGhostAll(){
  const tc=document.getElementById('ga-tc').value.trim();
  const names=document.getElementById('ga-names').value.trim();
  if(!tc){showRes('ga-res','⚠ Team code দিন!','error');return;}

  // get selected UIDs
  const selected=clientList.filter(uid=>{
    const cb=document.getElementById('gs-'+uid);
    return cb?cb.checked:true;
  });
  if(selected.length===0){showRes('ga-res','⚠ কোনো UID select করা নেই!','error');return;}

  setBtn('ga-btn',true,'','btn-purple');
  addLog(`Ghost All → TC:${tc} UIDs:[${selected.join(',')}] NAMES:${names||'auto'}`,'info');

  try{
    let url=`/ghost_all?teamcode=${encodeURIComponent(tc)}`;
    if(names)url+=`&ghost_names=${encodeURIComponent(names)}`;
    const r=await fetch(url);
    const d=await r.json();
    if(d.error){
      showRes('ga-res','❌ '+d.error,'error');
      addLog('FAIL: '+d.error,'fail');
      toast('❌ Failed!','var(--red)');
    } else {
      const res=d.results||{};
      const cnt=Object.keys(res).length;
      const minsStr=(22365447).toLocaleString();
      let txt=`✅ ${cnt} GHOSTS SENT!\n\n`;
      Object.entries(res).forEach(([uid,msg],i)=>{
        const cc=COLORS[i%COLORS.length];
        txt+=`• ${uid}: ${msg}\n`;
      });
      txt+=`\n⏱ Duration: ${minsStr} minutes each (∞ Forever)`;
      showRes('ga-res',txt,'success');
      totalSent+=cnt;totalGhosts+=cnt;
      document.getElementById('statSent').textContent=totalSent;
      document.getElementById('statGhosts').textContent=totalGhosts;
      addLog(`OK → ${cnt} ghosts sent`,'ok');
      toast(`👥 ${cnt} Ghosts sent!`,'var(--purple)');
    }
  }catch(e){
    showRes('ga-res','⚠ Network error: '+e.message,'error');
    addLog('Network error: '+e.message,'fail');
  }
  setBtn('ga-btn',false,'👥 SEND GHOST ALL','btn-purple');
}

// ═══════════════════════════════════════════════
// ADD CLIENT
// ═══════════════════════════════════════════════
async function addClient(){
  const uid=document.getElementById('c-uid').value.trim();
  const pass=document.getElementById('c-pass').value.trim();
  if(!uid||!pass){showRes('c-res','⚠ UID এবং Password দিন','error');return;}
  const btn=document.getElementById('c-add-btn');
  btn.disabled=true;
  btn.innerHTML='<span class="spin"></span>CONNECTING...';
  addLog(`Connecting: ${uid}`,'info');
  try{
    const r=await fetch(`/start_client?account_id=${encodeURIComponent(uid)}&password=${encodeURIComponent(pass)}`);
    const d=await r.json();
    if(d.error){
      showRes('c-res','❌ '+d.error,'error');
      addLog('FAIL: '+d.error,'fail');
      toast('❌ Failed to add','var(--red)');
    } else {
      showRes('c-res',`✅ ${d.message}\n\n✅ accounts.json এ save হয়েছে\n✅ UID online হয়েছে`,'success');
      addLog(`✅ ${uid} connected & saved to accounts.json`,'ok');
      toast(`✅ UID ${uid} added!`,'var(--green)');
      document.getElementById('c-uid').value='';
      document.getElementById('c-pass').value='';
      fetchClients();
      loadSavedAccs();
    }
  }catch(e){
    showRes('c-res','⚠ '+e.message,'error');
    toast('⚠ Error','var(--gold2)');
  }
  btn.disabled=false;
  btn.innerHTML='➕ ADD & CONNECT NOW';
}

// ═══════════════════════════════════════════════
// REMOVE CLIENT
// ═══════════════════════════════════════════════
async function removeClient(){
  const uid=document.getElementById('c-rm-id').value.trim();
  if(!uid){showRes('c-rm-res','⚠ UID দিন','error');return;}
  addLog(`Removing: ${uid}`,'warn');
  try{
    const r=await fetch(`/stop_client?account_id=${encodeURIComponent(uid)}`);
    const d=await r.json();
    if(d.error){
      showRes('c-rm-res','❌ '+d.error,'error');
    } else {
      showRes('c-rm-res','✅ '+d.message,'success');
      addLog(`Removed: ${uid}`,'ok');
      toast(`🗑 UID ${uid} removed`,'var(--gold2)');
      document.getElementById('c-rm-id').value='';
      fetchClients();
      loadSavedAccs();
    }
  }catch(e){showRes('c-rm-res','⚠ '+e.message,'error');}
}

// ═══════════════════════════════════════════════
// ENTER KEY
// ═══════════════════════════════════════════════
document.addEventListener('keydown',e=>{
  if(e.key!=='Enter')return;
  const act=document.querySelector('.panel.active');
  if(!act)return;
  if(act.id==='panel-ghost')sendGhost();
  else if(act.id==='panel-ghostall')sendGhostAll();
  else if(act.id==='panel-adduid')addClient();
});

// ═══════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════
addLog('NIROB GHOST VIP v4.0 loaded ✅','ok');
addLog('Ghost duration: 22,365,447 minutes = ∞ Forever','info');
addLog('Developer: @NIROB_353 | FF TCP Tool','info');

fetchClients();
setInterval(updateUptime,1000);
startRefresh();
</script>
</body>
</html>'''

# ==================== Serve embedded index.html ====================
@app.route('/')
def serve_index():
    from flask import Response
    return Response(INDEX_HTML, mimetype='text/html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# ==================== CORS ====================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

def parse_ghost_names(ghost_names_param):
    """Parse ghost names from either {name1}{name2} or comma-separated list"""
    if not ghost_names_param:
        return []
    if '{' in ghost_names_param and '}' in ghost_names_param:
        names = re.findall(r'\{(.*?)\}', ghost_names_param)
        return names
    names = [name.strip() for name in ghost_names_param.split(',') if name.strip()]
    return names

def AuTo_ResTartinG():
    return

def ResTarT_BoT():
    return

class TcpBotConnectMain:
    def __init__(self, account_id, password):
        self.account_id = account_id
        self.password = password
        self.key = None
        self.iv = None
        self.socket_client = None
        self.clientsocket = None
        self.running = False
        self.connection_attempts = 0
        self.max_connection_attempts = 2
        self.AutH = None
        self.DaTa2 = None
        self.sockf1_thread = None

    def run(self):
        if shutting_down:
            return
        if not hasattr(self, "auto_restart_thread_started"):
            t = threading.Thread(target=AuTo_ResTartinG, daemon=True)
            t.start()
            self.auto_restart_thread_started = True
        self.running = True
        self.connection_attempts = 0
        while (
            self.running
            and not shutting_down
            and self.connection_attempts < self.max_connection_attempts
        ):
            try:
                self.connection_attempts += 1
                print(f"[{self.account_id}] Connection attempt {self.connection_attempts}/{self.max_connection_attempts}")
                self.get_tok()
                break
            except Exception as e:
                print(f"[{self.account_id}] Error in run: {e}")
                if self.connection_attempts >= self.max_connection_attempts:
                    print(f"[{self.account_id}] Reached max connection attempts. Stopping.")
                    self.stop()
                    break
                print(f"[{self.account_id}] Retrying after 5 seconds...")
                time.sleep(5)

    def stop(self):
        self.running = False
        try:
            if self.clientsocket:
                self.clientsocket.close()
        except:
            pass
        try:
            if self.socket_client:
                self.socket_client.close()
        except:
            pass
        print(f"[{self.account_id}] Client stopped")

    def restart(self, delay=5):
        if shutting_down:
            return
        print(f"[{self.account_id}] Restarting client in {delay} seconds...")
        time.sleep(delay)
        self.run()

    def is_socket_connected(self, sock):
        try:
            if sock is None:
                return False
            writable = select.select([], [sock], [], 0.1)[1]
            if sock in writable:
                sock.send(b"")
                return True
            return False
        except (OSError, socket.error) as e:
            if e.errno == errno.EBADF:
                print(f"[{self.account_id}] Socket bad file descriptor")
            return False
        except Exception as e:
            print(f"[{self.account_id}] Socket check error: {e}")
            return False

    def ensure_connection(self):
        if not self.is_socket_connected(self.socket_client) and self.running:
            print(f"[{self.account_id}] Attempting to reconnect")
            self.restart(delay=2)
            return False
        return True

    def sockf1(self, tok, online_ip, online_port, packet, key, iv):
        while self.running and not shutting_down:
            try:
                self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_client.settimeout(30)
                self.socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                online_port = int(online_port)
                print(f"[{self.account_id}] Connecting to {online_ip}:{online_port}...")
                self.socket_client.connect((online_ip, online_port))
                print(f"[{self.account_id}] Connected to {online_ip}:{online_port}")
                self.socket_client.send(bytes.fromhex(tok))
                print(f"[{self.account_id}] Token sent successfully")
                while (
                    self.running
                    and not shutting_down
                    and self.is_socket_connected(self.socket_client)
                ):
                    try:
                        readable, _, _ = select.select([self.socket_client], [], [], 1.0)
                        if self.socket_client in readable:
                            self.DaTa2 = self.socket_client.recv(99999)
                            if not self.DaTa2:
                                print(f"[{self.account_id}] Server closed connection gracefully")
                                break
                            if (
                                "0500" in self.DaTa2.hex()[0:4]
                                and len(self.DaTa2.hex()) > 30
                            ):
                                try:
                                    self.packet = json.loads(
                                        DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}')
                                    )
                                    self.AutH = self.packet["5"]["data"]["7"]["data"]
                                    print(f"[{self.account_id}] 0500 packet received, AutH={self.AutH}")
                                except Exception as parse_err:
                                    print(f"[{self.account_id}] Error parsing 0500: {parse_err}")
                    except socket.timeout:
                        continue
                    except (OSError, socket.error) as e:
                        if e.errno == errno.EBADF:
                            print(f"[{self.account_id}] Bad file descriptor, reconnecting...")
                            break
                        else:
                            print(f"[{self.account_id}] Socket error: {e}. Reconnecting...")
                            break
                    except Exception as e:
                        print(f"[{self.account_id}] Unexpected error: {e}. Reconnecting...")
                        break
            except socket.timeout:
                print(f"[{self.account_id}] Connection timeout, retrying...")
            except (OSError, socket.error) as e:
                if e.errno == errno.EBADF:
                    print(f"[{self.account_id}] Bad file descriptor during connection")
                else:
                    print(f"[{self.account_id}] Connection error: {e}")
            except Exception as e:
                print(f"[{self.account_id}] Unexpected error: {e}")
            if self.running and not shutting_down:
                print(f"[{self.account_id}] Reconnecting to online server in 2 seconds...")
                time.sleep(2)

    def connect(self, tok, packet, key, iv, whisper_ip, whisper_port, online_ip, online_port):
        while self.running and not shutting_down:
            try:
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientsocket.settimeout(None)
                self.clientsocket.connect((whisper_ip, int(whisper_port)))
                print(f"[{self.account_id}] Connected to {whisper_ip}:{whisper_port}")
                self.clientsocket.send(bytes.fromhex(tok))
                self.data = self.clientsocket.recv(1024)
                self.clientsocket.send(get_packet2(self.key, self.iv))
                self.sockf1_thread = threading.Thread(
                    target=self.sockf1,
                    args=(tok, online_ip, online_port, "anything", key, iv),
                    daemon=True
                )
                self.sockf1_thread.start()
                while self.running and not shutting_down:
                    dataS = self.clientsocket.recv(1024)
                    if not dataS:
                        break
            except Exception as e:
                if not shutting_down:
                    print(f"[{self.account_id}] Error in connect: {e}. Retrying in 3 seconds...")
                    time.sleep(3)
            finally:
                if self.clientsocket:
                    try:
                        self.clientsocket.close()
                    except:
                        pass
                if self.running and not shutting_down:
                    print(f"[{self.account_id}] Reconnecting to whisper server in 2 seconds...")
                    time.sleep(2)

    def parse_my_message(self, serialized_data):
        MajorLogRes = MajorLoginRes()
        MajorLogRes.ParseFromString(serialized_data)
        timestamp = MajorLogRes.kts
        key = MajorLogRes.ak
        iv = MajorLogRes.aiv
        BASE64_TOKEN = MajorLogRes.token
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp, key, iv, BASE64_TOKEN

    def GET_PAYLOAD_BY_DATA(self, JWT_TOKEN, NEW_ACCESS_TOKEN, date):
        token_payload_base64 = JWT_TOKEN.split(".")[1]
        token_payload_base64 += "=" * ((4 - len(token_payload_base64) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode("utf-8")
        decoded_payload = json.loads(decoded_payload)
        NEW_EXTERNAL_ID = decoded_payload["external_id"]
        SIGNATURE_MD5 = decoded_payload["signature_md5"]
        now = datetime.now()
        now = str(now)[: len(str(now)) - 7]
        formatted_time = date
        payload = bytes.fromhex(Payload1A13)
        payload = payload.replace(b"2025-08-02 17:15:04", str(now).encode())
        payload = payload.replace(
            b"10e299be9f8199bd50f8c52bbae4695bc1935563ba17d3859c97237bd45cb428",
            NEW_ACCESS_TOKEN.encode("UTF-8"),
        )
        payload = payload.replace(
            b"b70245b92be827af56d8932346f351f2", NEW_EXTERNAL_ID.encode("UTF-8")
        )
        payload = payload.replace(
            b"7428b253defc164018c604a1ebbfebdf", SIGNATURE_MD5.encode("UTF-8")
        )
        PAYLOAD = payload.hex()
        PAYLOAD = encrypt_api(PAYLOAD)
        PAYLOAD = bytes.fromhex(PAYLOAD)
        whisper_ip, whisper_port, online_ip, online_port = self.GET_LOGIN_DATA(JWT_TOKEN, PAYLOAD)
        return whisper_ip, whisper_port, online_ip, online_port

    def GET_LOGIN_DATA(self, JWT_TOKEN, PAYLOAD):
        url = GetLoginDataRegion
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {JWT_TOKEN}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": FreeFireVersion,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "Host": "client.ind.freefiremobile",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br",
        }
        max_retries = 3
        attempt = 0
        while attempt < max_retries and not shutting_down:
            try:
                response = requests.post(url, headers=headers, data=PAYLOAD, verify=False)
                response.raise_for_status()
                x = response.content.hex()
                json_result = get_available_room(x)
                parsed_data = json.loads(json_result)
                whisper_address = parsed_data["32"]["data"]
                online_address = parsed_data["14"]["data"]
                online_ip = online_address[: len(online_address) - 6]
                whisper_ip = whisper_address[: len(whisper_address) - 6]
                online_port = int(online_address[len(online_address) - 5 :])
                whisper_port = int(whisper_address[len(whisper_address) - 5 :])
                return whisper_ip, whisper_port, online_ip, online_port
            except requests.RequestException as e:
                print(f"[{self.account_id}] Request failed: {e}. Attempt {attempt + 1} of {max_retries}. Retrying...")
                attempt += 1
                time.sleep(2)
        print(f"[{self.account_id}] Failed to get login data after multiple attempts.")
        return None, None, None, None

    def guest_token(self, uid, password):
        url = "https://ffmconnect.ggpolarbear.com/oauth/guest/token/grant"
        headers = {
            "Host": "ffmconnect.ggpolarbear.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 10;en;EN;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067",
        }
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        NEW_ACCESS_TOKEN = data["access_token"]
        NEW_OPEN_ID = data["open_id"]
        OLD_ACCESS_TOKEN = "10e299be9f8199bd50f8c52bbae4695bc1935563ba17d3859c97237bd45cb428"
        OLD_OPEN_ID = "b70245b92be827af56d8932346f351f2"
        time.sleep(0.2)
        data = self.TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid)
        return data

    def TOKEN_MAKER(self, OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, id):
        headers = {
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": FreeFireVersion,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-GA": "v1 1",
            "Content-Length": "928",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
            "Host": "loginbp.ggpolarbear.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
        data = bytes.fromhex(Payload1A13)
        data = data.replace(b"1.123.1", b"1.123.1")
        data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
        data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
        hex_data = data.hex()
        encrypted_data = encrypt_api(hex_data)
        Final_Payload = bytes.fromhex(encrypted_data)
        URL = MajorLoginRegion
        RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False)
        combined_timestamp, key, iv, BASE64_TOKEN = self.parse_my_message(RESPONSE.content)
        if RESPONSE.status_code == 200:
            if len(RESPONSE.text) < 10:
                return False
            whisper_ip, whisper_port, online_ip, online_port = self.GET_PAYLOAD_BY_DATA(
                BASE64_TOKEN, NEW_ACCESS_TOKEN, 1
            )
            self.key = key
            self.iv = iv
            print(f"[{self.account_id}] Key: {key}, IV: {iv}")
            return (BASE64_TOKEN, key, iv, combined_timestamp, whisper_ip, whisper_port, online_ip, online_port)
        else:
            return False

    def get_tok(self):
        token_data = self.guest_token(self.account_id, self.password)
        if not token_data:
            print(f"[{self.account_id}] Failed to get token")
            self.restart()
            return
        token, key, iv, Timestamp, whisper_ip, whisper_port, online_ip, online_port = token_data
        print(f"[{self.account_id}] Whisper: {whisper_ip}:{whisper_port}")
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            account_id = decoded.get("account_id")
            encoded_acc = hex(account_id)[2:]
            hex_value = self.dec_to_hex(Timestamp)
            time_hex = hex_value
            BASE64_TOKEN_ = token.encode().hex()
            print(f"[{self.account_id}] Token decoded. Account ID: {account_id}")
        except Exception as e:
            print(f"[{self.account_id}] Error processing token: {e}")
            self.restart()
            return
        try:
            head = hex(len(encrypt_packet(BASE64_TOKEN_, key, iv)) // 2)[2:]
            length = len(encoded_acc)
            zeros = "00000000"
            if length == 9:
                zeros = "0000000"
            elif length == 8:
                zeros = "00000000"
            elif length == 10:
                zeros = "000000"
            elif length == 7:
                zeros = "000000000"
            else:
                print(f"[{self.account_id}] Unexpected length encountered")
            head = f"0115{zeros}{encoded_acc}{time_hex}00000{head}"
            final_token = head + encrypt_packet(BASE64_TOKEN_, key, iv)
        except Exception as e:
            print(f"[{self.account_id}] Error creating final token: {e}")
            self.restart()
            return
        self.connect(final_token, "anything", key, iv, whisper_ip, whisper_port, online_ip, online_port)
        return final_token, key, iv

    def dec_to_hex(self, ask):
        ask_result = hex(ask)
        final_result = str(ask_result)[2:]
        if len(final_result) == 1:
            final_result = "0" + final_result
            return final_result
        else:
            return final_result

    def execute_command(self, command, *args):
        if command == "/XRRR":
            try:
                if not self.socket_client or not self.is_socket_connected(self.socket_client):
                    return "Socket not connected, please wait for connection..."
                team_code = args[0] if len(args) > 0 else None
                account_name = args[1] if len(args) > 1 else "UnknownGhost"
                if not team_code:
                    return "No team code provided for /XRRR"
                print(f"[{self.account_id}] Executing /XRRR for team code {team_code} with name {account_name}")
                sys.stdout.flush()
                self.socket_client.send(GenJoinSquadsPacket(team_code, self.key, self.iv))
                time.sleep(0.5)
                start_time = time.time()
                got_0500 = False
                idT = None
                sq = None
                while not got_0500 and (time.time() - start_time) < 10:
                    if (
                        self.DaTa2
                        and len(self.DaTa2.hex()) >= 4
                        and "0500" in self.DaTa2.hex()[0:4]
                    ):
                        try:
                            self.dT = json.loads(DeCode_PackEt(self.DaTa2.hex()[10:]))
                            if (
                                "5" in self.dT
                                and "data" in self.dT["5"]
                                and "31" in self.dT["5"]["data"]
                                and "1" in self.dT["5"]["data"]
                            ):
                                sq = self.dT["5"]["data"]["31"]["data"]
                                idT = self.dT["5"]["data"]["1"]["data"]
                                got_0500 = True
                                print(f"[{self.account_id}] Got 0500 with ID: {idT}")
                                break
                        except Exception as parse_err:
                            print(f"[{self.account_id}] Error parsing 0500: {parse_err}")
                    time.sleep(0.1)
                if not got_0500:
                    return f"Failed to get 0500 for team code {team_code} within timeout"
                self.socket_client.send(ExiT("000000", self.key, self.iv))
                time.sleep(0.1)
                self.socket_client.send(ghost_pakcet(idT, account_name, sq, self.key, self.iv))
                time.sleep(0.1)
                self.socket_client.send(ExiT("000000", self.key, self.iv))
                return f"Ghost {account_name} successfully joined squad {idT} (original code {team_code})"
            except Exception as e:
                print(f"[{self.account_id}] Error in execute_command: {e}")
                return f"Error executing command: {e}"
        else:
            return f"Unknown command: {command}"


def load_accounts(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def cleanup():
    global shutting_down
    shutting_down = True
    print("Shutting down all clients...")
    for account_id, client in list(clients.items()):
        client.stop()
        del clients[account_id]
    print("Cleanup completed")


@app.route("/start_client", methods=["GET"])
def start_client():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    account_id = request.args.get("account_id")
    password = request.args.get("password")
    if not account_id or not password:
        return jsonify({"error": "Account ID and password are required"}), 400
    if account_id in clients:
        return jsonify({"error": "Client already running"}), 400
    client = TcpBotConnectMain(account_id, password)
    clients[account_id] = client
    client_thread = threading.Thread(target=client.run)
    client_thread.daemon = True
    client_thread.start()
    return jsonify({"message": f"Client {account_id} started successfully"}), 200


@app.route("/stop_client", methods=["GET"])
def stop_client():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    account_id = request.args.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    if account_id not in clients:
        return jsonify({"error": "Client not found"}), 404
    client = clients[account_id]
    client.stop()
    del clients[account_id]
    return jsonify({"message": f"Client {account_id} stopped successfully"}), 200


@app.route("/execute_command", methods=["GET"])
def execute_command():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    account_id = request.args.get("account_id")
    command = request.args.get("command")
    client_id = request.args.get("client_id")
    name = request.args.get("name")
    if not account_id or not command:
        return jsonify({"error": "Account ID and command are required"}), 400
    if account_id not in clients:
        return jsonify({"error": "Client not found"}), 404
    client = clients[account_id]
    args = []
    if client_id:
        try:
            args.append(int(client_id))
        except ValueError:
            return jsonify({"error": "Invalid client_id format"}), 400
    if name:
        args.append(name)
    result = client.execute_command(command, *args)
    return jsonify({"result": result}), 200


@app.route("/list_clients", methods=["GET"])
def list_clients():
    return jsonify({"clients": list(clients.keys())}), 200


@app.route("/execute_command_all", methods=["GET"])
def execute_command_all():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    command = request.args.get("command")
    ghost_names_param = request.args.get("ghost_names", None)
    if not command:
        return jsonify({"error": "Command parameter is required"}), 400
    command = command.strip()
    cmd = None
    arg = None
    if "=" in command:
        parts = command.split("=", 1)
        cmd = parts[0].strip()
        arg = parts[1].strip() if len(parts) > 1 else None
    else:
        parts = command.split(" ", 1)
        cmd = parts[0].strip()
        arg = parts[1].strip() if len(parts) > 1 else None
    ghost_names_list = parse_ghost_names(ghost_names_param)
    sorted_clients = sorted(clients.items(), key=lambda x: int(x[0]))
    results = {}
    for idx, (account_id, client) in enumerate(sorted_clients):
        if ghost_names_list:
            if len(ghost_names_list) == 1:
                account_name = ghost_names_list[0]
            else:
                if idx < len(ghost_names_list):
                    account_name = ghost_names_list[idx]
                else:
                    account_name = ghost_names_list[-1]
        else:
            account_name = str(account_id)
        if cmd == "/XRRR" and arg:
            result = client.execute_command(cmd, arg, account_name)
            results[account_id] = f"Dev: ROHIT | {result} | Name: {account_name}"
        else:
            results[account_id] = f"Unknown or invalid command: {command} | Name: {account_name}"
    return jsonify({"results": results})


@app.route("/ghost_all", methods=["GET"])
def ghost_all():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    teamcode = request.args.get("teamcode")
    ghost_names_param = request.args.get("ghost_names", "")
    if not teamcode:
        return jsonify({"error": "teamcode parameter is required"}), 400
    ghost_names_list = parse_ghost_names(ghost_names_param)
    sorted_clients = sorted(clients.items(), key=lambda x: int(x[0]))
    results = {}
    for idx, (account_id, client) in enumerate(sorted_clients):
        if ghost_names_list:
            if len(ghost_names_list) == 1:
                account_name = ghost_names_list[0]
            else:
                account_name = ghost_names_list[idx] if idx < len(ghost_names_list) else ghost_names_list[-1]
        else:
            account_name = str(account_id)
        result = client.execute_command("/XRRR", teamcode, account_name)
        results[account_id] = f"Dev: ROHIT | {result} | Name: {account_name}"
    return jsonify({"results": results})


@app.route("/ghost", methods=["GET"])
def ghost():
    if shutting_down:
        return jsonify({"error": "Server is shutting down"}), 503
    teamcode = request.args.get("teamcode")
    ghost_name = request.args.get("ghost_name")
    if not teamcode:
        return jsonify({"error": "teamcode parameter is required"}), 400
    if not ghost_name:
        ghost_name = "Ghost"
    if not clients:
        return jsonify({"error": "No clients available"}), 500
    account_id, client = next(iter(sorted(clients.items(), key=lambda x: int(x[0]))))
    result = client.execute_command("/XRRR", teamcode, ghost_name)
    return jsonify({
        "account_id": account_id,
        "result": f"Dev: ROHIT | {result} | Name: {ghost_name}"
    })


@app.route("/shutdown", methods=["GET"])
def shutdown_server():
    global shutting_down
    shutting_down = True
    cleanup()
    return jsonify({"message": "Server shutdown initiated"}), 200


def signal_handler(sig, frame):
    print("Received shutdown signal")
    cleanup()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)

    if os.getenv("RENDER") != "true":
        try:
            accounts = load_accounts("accounts.json")
            for account_id, password in accounts.items():
                client = TcpBotConnectMain(account_id, password)
                clients[account_id] = client
                threading.Thread(target=client.run, daemon=True).start()
                time.sleep(2)
        except FileNotFoundError:
            print("No accounts file found. Starting without preloaded accounts.")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIROB GHOST</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #00f5ff;
            --secondary: #bf00ff;
            --accent: #ff006e;
            --bg: #020010;
            --card-bg: rgba(0, 5, 30, 0.92);
            --border: rgba(0, 245, 255, 0.15);
            --glow: 0 0 20px rgba(0, 245, 255, 0.3);
            --glow2: 0 0 20px rgba(191, 0, 255, 0.3);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Rajdhani', sans-serif;
            background: var(--bg);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        /* ---- BACKGROUND ---- */
        #bgCanvas {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 0;
        }

        .grid-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 0;
            background-image:
                linear-gradient(rgba(0,245,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,245,255,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
        }

        /* ---- CARD ---- */
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(30px);
            border-radius: 24px;
            padding: 36px 28px;
            max-width: 460px;
            width: 100%;
            border: 1px solid var(--border);
            box-shadow: 0 0 60px rgba(0,245,255,0.08), 0 30px 80px #00000099, inset 0 1px 0 rgba(255,255,255,0.05);
            position: relative;
            z-index: 1;
        }

        .card::before {
            content: '';
            position: absolute;
            top: -1px; left: 20%; right: 20%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
            border-radius: 2px;
        }

        /* ---- HEADER ---- */
        .header {
            text-align: center;
            margin-bottom: 24px;
        }

        .ghost-icon-wrap {
            position: relative;
            display: inline-block;
            margin-bottom: 12px;
        }

        .ghost-icon-wrap i {
            font-size: 52px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 16px rgba(0,245,255,0.6));
            animation: floatGhost 3s ease-in-out infinite;
        }

        .ghost-ring {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 80px; height: 80px;
            border: 1px solid rgba(0,245,255,0.2);
            border-radius: 50%;
            animation: ringPulse 2s ease-out infinite;
        }

        @keyframes floatGhost {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }

        @keyframes ringPulse {
            0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.8; }
            100% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; }
        }

        h1 {
            font-family: 'Orbitron', monospace;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 4px;
            background: linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: none;
            line-height: 1.1;
        }

        h1 span {
            font-size: 16px;
            font-weight: 400;
            letter-spacing: 8px;
            background: linear-gradient(90deg, rgba(0,245,255,0.6), rgba(191,0,255,0.6));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: block;
            margin-top: 4px;
        }

        /* ---- REFRESH COUNTDOWN ---- */
        .refresh-bar-wrap {
            margin: 10px 0 20px;
            position: relative;
        }

        .refresh-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: rgba(0,245,255,0.5);
            font-family: 'Orbitron', monospace;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }

        .refresh-label span:last-child {
            color: var(--primary);
            font-weight: 700;
        }

        .refresh-bar-bg {
            width: 100%;
            height: 3px;
            background: rgba(255,255,255,0.05);
            border-radius: 2px;
            overflow: hidden;
        }

        .refresh-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 2px;
            transition: width 1s linear;
            box-shadow: 0 0 8px var(--primary);
        }

        /* ---- COLOR PICKER ---- */
        .color-picker {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        .color-dot {
            width: 22px; height: 22px;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid transparent;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }

        .color-dot:hover { transform: scale(1.25); }
        .color-dot.active { border-color: #fff; box-shadow: 0 0 10px currentColor; }

        /* ---- TABS ---- */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 4px;
            border: 1px solid rgba(255,255,255,0.05);
        }

        .tab {
            flex: 1;
            padding: 12px;
            background: transparent;
            border: none;
            border-radius: 13px;
            color: rgba(255,255,255,0.4);
            font-family: 'Orbitron', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }

        .tab.active {
            background: linear-gradient(135deg, rgba(0,245,255,0.15), rgba(191,0,255,0.15));
            color: var(--primary);
            box-shadow: 0 0 20px rgba(0,245,255,0.1);
            border: 1px solid rgba(0,245,255,0.2);
        }

        .tab i { margin-right: 6px; }

        /* ---- INPUTS ---- */
        .input-group { margin-bottom: 16px; }

        label {
            color: rgba(0,245,255,0.6);
            font-size: 10px;
            font-family: 'Orbitron', monospace;
            letter-spacing: 2px;
            text-transform: uppercase;
            display: block;
            margin-bottom: 8px;
        }

        label i { margin-right: 6px; }

        input {
            width: 100%;
            padding: 14px 16px;
            background: rgba(0,0,0,0.4);
            border: 1px solid rgba(0,245,255,0.1);
            border-radius: 14px;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 16px;
            font-weight: 500;
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(0,245,255,0.1), inset 0 0 10px rgba(0,245,255,0.03);
        }

        input::placeholder { color: rgba(255,255,255,0.2); }

        /* ---- BUTTON ---- */
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: #000;
            font-family: 'Orbitron', monospace;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 3px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 20px 0 16px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 30px rgba(0,245,255,0.25);
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
            transition: left 0.5s;
        }

        .btn:hover::before { left: 100%; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 40px rgba(0,245,255,0.4); }
        .btn:disabled { opacity: 0.6; transform: none; cursor: not-allowed; }

        /* ---- STATUS BAR ---- */
        .status-bar {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            margin-top: 4px;
        }

        .stat-box {
            background: rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 12px 8px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .stat-box::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            opacity: 0.4;
        }

        .stat-value {
            font-family: 'Orbitron', monospace;
            font-size: 22px;
            font-weight: 900;
            color: var(--primary);
            line-height: 1;
            text-shadow: 0 0 12px var(--primary);
        }

        .stat-value.ghost-val { color: var(--secondary); text-shadow: 0 0 12px var(--secondary); }
        .stat-value.success-val { color: #00ff88; text-shadow: 0 0 12px #00ff88; }

        .stat-label {
            font-size: 9px;
            color: rgba(255,255,255,0.35);
            font-family: 'Orbitron', monospace;
            letter-spacing: 1px;
            margin-top: 4px;
            text-transform: uppercase;
        }

        .live-dot {
            display: inline-block;
            width: 6px; height: 6px;
            border-radius: 50%;
            background: #00ff88;
            margin-right: 4px;
            animation: liveBlink 1.2s ease-in-out infinite;
            vertical-align: middle;
        }

        .live-dot.offline { background: var(--accent); animation: none; }

        @keyframes liveBlink {
            0%, 100% { opacity: 1; box-shadow: 0 0 6px #00ff88; }
            50% { opacity: 0.3; box-shadow: none; }
        }

        /* ---- CLIENTS LIST ---- */
        .clients-section {
            margin-top: 18px;
            border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 14px;
        }

        .clients-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .clients-title {
            font-family: 'Orbitron', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            color: rgba(0,245,255,0.5);
            text-transform: uppercase;
        }

        .refresh-btn {
            background: rgba(0,245,255,0.08);
            border: 1px solid rgba(0,245,255,0.15);
            color: var(--primary);
            padding: 5px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 10px;
            font-family: 'Orbitron', monospace;
            letter-spacing: 1px;
            transition: all 0.2s;
        }

        .refresh-btn:hover {
            background: rgba(0,245,255,0.15);
            box-shadow: 0 0 12px rgba(0,245,255,0.2);
        }

        .clients-list {
            max-height: 140px;
            overflow-y: auto;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.04);
            padding: 4px;
            scrollbar-width: thin;
            scrollbar-color: rgba(0,245,255,0.2) transparent;
        }

        .client-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            font-size: 12px;
            font-family: 'Rajdhani', sans-serif;
            transition: background 0.2s;
        }

        .client-item:hover { background: rgba(0,245,255,0.03); border-radius: 8px; }
        .client-item:last-child { border-bottom: none; }

        .client-id {
            color: rgba(255,255,255,0.7);
            font-weight: 600;
            font-size: 13px;
        }

        .client-id i { color: var(--secondary); margin-right: 6px; }

        .client-status {
            color: #00ff88;
            font-size: 10px;
            font-family: 'Orbitron', monospace;
            letter-spacing: 1px;
        }

        .empty-list {
            text-align: center;
            color: rgba(255,255,255,0.2);
            padding: 16px 10px;
            font-size: 12px;
            font-family: 'Orbitron', monospace;
            letter-spacing: 1px;
        }

        /* ---- MSG BOX ---- */
        .msg {
            padding: 14px 16px;
            border-radius: 14px;
            margin-top: 14px;
            display: none;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.5px;
        }

        .msg.success {
            background: rgba(0,255,136,0.1);
            border: 1px solid rgba(0,255,136,0.3);
            color: #00ff88;
            display: block;
        }

        .msg.error {
            background: rgba(255,0,110,0.1);
            border: 1px solid rgba(255,0,110,0.3);
            color: #ff4d6d;
            display: block;
        }

        .msg.info {
            background: rgba(0,245,255,0.08);
            border: 1px solid rgba(0,245,255,0.2);
            color: var(--primary);
            display: block;
        }

        /* ---- SPINNER ---- */
        .spinner {
            width: 18px; height: 18px;
            border: 2px solid rgba(0,0,0,0.2);
            border-top-color: #000;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* ---- FOOTER ---- */
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.15);
            font-size: 10px;
            font-family: 'Orbitron', monospace;
            letter-spacing: 2px;
            margin-top: 20px;
            text-transform: uppercase;
        }

        .footer span { color: var(--primary); opacity: 0.4; }

        /* ---- OFFLINE OVERLAY ---- */
        #offlineOverlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(2,0,16,0.96);
            z-index: 9999;
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 20px;
        }

        #offlineOverlay.show { display: flex; }

        .offline-text {
            font-family: 'Orbitron', monospace;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 4px;
            color: var(--primary);
            text-shadow: 0 0 20px var(--primary);
            animation: pulse 1s ease-in-out infinite;
        }

        .offline-sub {
            font-family: 'Orbitron', monospace;
            font-size: 11px;
            color: rgba(0,245,255,0.4);
            letter-spacing: 2px;
        }

        .offline-counter {
            font-family: 'Orbitron', monospace;
            font-size: 40px;
            font-weight: 900;
            color: var(--secondary);
            text-shadow: 0 0 30px var(--secondary);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* ---- SCAN LINE EFFECT ---- */
        body::after {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 9998;
            background: repeating-linear-gradient(
                0deg,
                rgba(0,0,0,0.015) 0px,
                rgba(0,0,0,0.015) 1px,
                transparent 1px,
                transparent 2px
            );
        }
    </style>
</head>
<body>

<canvas id="bgCanvas"></canvas>
<div class="grid-overlay"></div>

<!-- 7-min offline overlay -->
<div id="offlineOverlay">
    <div class="offline-text">⟳ SYSTEM REFRESH</div>
    <div class="offline-counter" id="overlayCount">5</div>
    <div class="offline-sub">RECONNECTING... PLEASE WAIT</div>
</div>

<div class="card">

    <!-- HEADER -->
    <div class="header">
        <div class="ghost-icon-wrap">
            <div class="ghost-ring"></div>
            <i class="fas fa-ghost"></i>
        </div>
        <h1>NIROB<span>G H O S T</span></h1>
    </div>

    <!-- 7-MIN REFRESH BAR -->
    <div class="refresh-bar-wrap">
        <div class="refresh-label">
            <span><i class="fas fa-sync-alt"></i> AUTO REFRESH</span>
            <span id="refreshCountdown">7:00</span>
        </div>
        <div class="refresh-bar-bg">
            <div class="refresh-bar-fill" id="refreshBar" style="width:100%"></div>
        </div>
    </div>

    <!-- COLOR PICKER -->
    <div class="color-picker">
        <div class="color-dot active" style="background:#00f5ff" onclick="changeTheme('#00f5ff','#bf00ff',this)"></div>
        <div class="color-dot" style="background:#00ff88" onclick="changeTheme('#00ff88','#00b4d8',this)"></div>
        <div class="color-dot" style="background:#bf00ff" onclick="changeTheme('#bf00ff','#ff006e',this)"></div>
        <div class="color-dot" style="background:#ff006e" onclick="changeTheme('#ff006e','#ff9f1c',this)"></div>
        <div class="color-dot" style="background:#ff9f1c" onclick="changeTheme('#ff9f1c','#ffee32',this)"></div>
        <div class="color-dot" style="background:#f72585" onclick="changeTheme('#f72585','#b5179e',this)"></div>
        <div class="color-dot" style="background:#3a86ff" onclick="changeTheme('#3a86ff','#8338ec',this)"></div>
    </div>

    <!-- TABS -->
    <div class="tabs">
        <button class="tab active" id="tabAll" onclick="setMode(\'all\')">
            <i class="fas fa-users"></i> GHOST ALL
        </button>
        <button class="tab" id="tabOne" onclick="setMode(\'one\')">
            <i class="fas fa-user-secret"></i> ONLY GHOST
        </button>
    </div>

    <!-- INPUTS -->
    <div class="input-group">
        <label><i class="fas fa-hashtag"></i> Team Code</label>
        <input type="text" id="teamcode" placeholder="Enter team code..." autocomplete="off">
    </div>

    <div class="input-group">
        <label><i class="fas fa-signature"></i> Ghost Name</label>
        <input type="text" id="ghostName" placeholder="Enter ghost name..." autocomplete="off" maxlength="12">
    </div>

    <!-- ACTION BUTTON -->
    <button class="btn" id="actionBtn" onclick="execute()">
        <i class="fas fa-ghost"></i>
        <span id="btnText">SEND GHOST ALL</span>
    </button>

    <!-- LIVE STATS -->
    <div class="status-bar">
        <div class="stat-box">
            <div class="stat-value" id="clientCount">0</div>
            <div class="stat-label"><span class="live-dot" id="liveDot"></span>ONLINE</div>
        </div>
        <div class="stat-box">
            <div class="stat-value ghost-val" id="ghostSent">0</div>
            <div class="stat-label">GHOST SENT</div>
        </div>
        <div class="stat-box">
            <div class="stat-value success-val" id="ghostSuccess">0</div>
            <div class="stat-label">JOINED</div>
        </div>
    </div>

    <!-- CLIENTS LIST -->
    <div class="clients-section">
        <div class="clients-header">
            <div class="clients-title"><i class="fas fa-network-wired"></i>&nbsp; Active IDs</div>
            <button class="refresh-btn" onclick="checkStatus()">
                <i class="fas fa-sync-alt"></i> REFRESH
            </button>
        </div>
        <div class="clients-list" id="clientsList">
            <div class="empty-list">LOADING...</div>
        </div>
    </div>

    <div id="msgBox" class="msg"></div>

    <div class="footer">NIROB GHOST &nbsp;<span>v4.0</span>&nbsp; PREMIUM UNLIMITED</div>
</div>

<script>
    let mode = 'all';
    let ghostSentCount = 0;
    let ghostSuccessCount = 0;
    const REFRESH_MS = 7 * 60 * 1000; // 7 minutes
    let refreshStart = Date.now();

    // ---- THEME ----
    function changeTheme(primary, secondary, el) {
        document.documentElement.style.setProperty('--primary', primary);
        document.documentElement.style.setProperty('--secondary', secondary);
        matrixPrimary = primary;
        document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
        el.classList.add('active');
    }

    // ---- MATRIX BG ----
    const canvas = document.getElementById('bgCanvas');
    const ctx = canvas.getContext('2d');
    let matrixPrimary = '#00f5ff';
    const chars = 'NIROB01GHOST'.split('');
    const fs = 14;
    let drops = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        drops = Array(Math.floor(canvas.width / fs)).fill(1);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    function drawMatrix() {
        ctx.fillStyle = 'rgba(2,0,16,0.06)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = matrixPrimary + '55';
        ctx.font = fs + 'px monospace';
        drops.forEach((y, i) => {
            ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * fs, y * fs);
            if (y * fs > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        });
    }
    setInterval(drawMatrix, 35);

    // ---- TABS ----
    function setMode(m) {
        mode = m;
        document.getElementById('tabAll').classList.toggle('active', m === 'all');
        document.getElementById('tabOne').classList.toggle('active', m === 'one');
        document.getElementById('btnText').textContent = m === 'all' ? 'SEND GHOST ALL' : 'SEND GHOST';
    }

    // ---- MSG ----
    function showMsg(text, type) {
        const m = document.getElementById('msgBox');
        m.innerHTML = text;
        m.className = 'msg ' + type;
        setTimeout(() => m.className = 'msg', 5000);
    }

    function clearInputs() {
        document.getElementById('teamcode').value = '';
        document.getElementById('ghostName').value = '';
    }

    // ---- EXECUTE ----
    async function execute() {
        let code = document.getElementById('teamcode').value.trim();
        let name = document.getElementById('ghostName').value.trim();
        if (name.length > 12) name = name.substring(0, 12);
        if (!code) { showMsg('⚠ Enter Team Code', 'error'); return; }
        if (!name) { showMsg('⚠ Enter Ghost Name', 'error'); return; }

        const btn = document.getElementById('actionBtn');
        btn.innerHTML = '<span class="spinner"></span>&nbsp; SENDING...';
        btn.disabled = true;

        ghostSentCount++;
        document.getElementById('ghostSent').textContent = ghostSentCount;

        try {
            let url = mode === 'all'
                ? `/ghost_all?teamcode=${encodeURIComponent(code)}&ghost_names=${encodeURIComponent(name)}`
                : `/ghost?teamcode=${encodeURIComponent(code)}&ghost_name=${encodeURIComponent(name)}`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.results) {
                const vals = Object.values(data.results);
                const ok = vals.filter(r => r && r.includes('successfully')).length;
                ghostSuccessCount += ok;
                document.getElementById('ghostSuccess').textContent = ghostSuccessCount;
                showMsg(`✅ ${ok}/${vals.length} Ghost joined group`, 'success');
                clearInputs();
            } else if (data.result) {
                if (data.result.includes('successfully')) {
                    ghostSuccessCount++;
                    document.getElementById('ghostSuccess').textContent = ghostSuccessCount;
                    showMsg(`✅ Ghost joined group`, 'success');
                } else {
                    showMsg(`❌ ${data.result}`, 'error');
                }
                clearInputs();
            } else if (data.error) {
                showMsg(`❌ ${data.error}`, 'error');
            } else {
                showMsg('⚠ Unexpected response', 'error');
            }
            checkStatus();
        } catch (e) {
            showMsg('❌ Connection error', 'error');
        } finally {
            btn.innerHTML = '<i class="fas fa-ghost"></i> <span id="btnText">' + (mode === 'all' ? 'SEND GHOST ALL' : 'SEND GHOST') + '</span>';
            btn.disabled = false;
        }
    }

    // ---- CHECK STATUS ----
    async function checkStatus() {
        try {
            const res = await fetch('/list_clients');
            if (!res.ok) throw new Error();
            const data = await res.json();
            const cls = data.clients || [];
            document.getElementById('clientCount').textContent = cls.length;
            const dot = document.getElementById('liveDot');

            if (cls.length > 0) {
                dot.className = 'live-dot';
                document.getElementById('clientsList').innerHTML = cls.map(id => `
                    <div class="client-item">
                        <span class="client-id"><i class="fas fa-circle" style="font-size:7px;color:#00ff88"></i> &nbsp;${id}</span>
                        <span class="client-status">● ONLINE</span>
                    </div>
                `).join('');
            } else {
                dot.className = 'live-dot offline';
                document.getElementById('clientsList').innerHTML = '<div class="empty-list">NO ACTIVE IDs</div>';
            }
        } catch (e) {
            document.getElementById('liveDot').className = 'live-dot offline';
            document.getElementById('clientCount').textContent = '0';
            document.getElementById('clientsList').innerHTML = '<div class="empty-list" style="color:rgba(255,0,110,0.5)">⚠ SERVER OFFLINE</div>';
        }
    }

    // ---- 7-MIN AUTO REFRESH ----
    const TOTAL_SECS = 7 * 60;
    let secsLeft = TOTAL_SECS;

    function updateRefreshBar() {
        secsLeft--;
        if (secsLeft <= 0) {
            triggerRefresh();
            return;
        }
        const pct = (secsLeft / TOTAL_SECS) * 100;
        document.getElementById('refreshBar').style.width = pct + '%';
        const m = Math.floor(secsLeft / 60);
        const s = secsLeft % 60;
        document.getElementById('refreshCountdown').textContent = m + ':' + String(s).padStart(2, '0');
    }

    function triggerRefresh() {
        const overlay = document.getElementById('offlineOverlay');
        overlay.classList.add('show');
        let cnt = 5;
        document.getElementById('overlayCount').textContent = cnt;
        const iv = setInterval(() => {
            cnt--;
            document.getElementById('overlayCount').textContent = cnt;
            if (cnt <= 0) {
                clearInterval(iv);
                // Reset stats
                ghostSentCount = 0;
                ghostSuccessCount = 0;
                document.getElementById('ghostSent').textContent = '0';
                document.getElementById('ghostSuccess').textContent = '0';
                secsLeft = TOTAL_SECS;
                document.getElementById('refreshBar').style.width = '100%';
                document.getElementById('refreshCountdown').textContent = '7:00';
                overlay.classList.remove('show');
                checkStatus();
            }
        }, 1000);
    }

    setInterval(updateRefreshBar, 1000);
    setInterval(checkStatus, 5000);

    // ---- KEY EVENTS ----
    document.getElementById('teamcode').addEventListener('keypress', e => { if (e.key === 'Enter') execute(); });
    document.getElementById('ghostName').addEventListener('keypress', e => { if (e.key === 'Enter') execute(); });
    document.getElementById('ghostName').addEventListener('input', function() {
        if (this.value.length > 12) this.value = this.value.slice(0, 12);
    });

    window.onload = () => { setMode('all'); checkStatus(); };
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

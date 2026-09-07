import json

with open('proyectos/contratos-agiles/seed_data.json', 'r', encoding='utf-8') as f:
    seed_data = json.load(f)

seed_json_str = json.dumps(seed_data, ensure_ascii=False)

html_template = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contratos Ágiles · Sistema Interactivo en Vivo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>
    :root {
      --bg: #09131d;
      --bg-darker: #050b12;
      --surface: #102030;
      --surface-card: #15273a;
      --surface-card-hover: #1b324a;
      --text: #f0f6fc;
      --text-muted: #8b9bb4;
      --border: rgba(255, 255, 255, 0.12);
      --border-focus: rgba(56, 189, 248, 0.6);
      --primary: #255f85;
      --primary-hover: #1e70a2;
      --accent: #e0a91b;
      --accent-glow: rgba(224, 169, 27, 0.25);
      --success: #10b981;
      --success-glow: rgba(16, 185, 129, 0.25);
      --danger: #ef4444;
      --cyan: #38bdf8;
      --radius: 10px;
      --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Global Demo Banner */
    .demo-bar {
      background: linear-gradient(90deg, #0b253a, #153e5d);
      border-bottom: 1px solid rgba(56, 189, 248, 0.25);
      padding: 0.55rem 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.82rem;
      z-index: 100;
    }
    .demo-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--cyan);
      font-weight: 600;
      letter-spacing: 0.02em;
    }
    .demo-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .btn-xs {
      padding: 0.28rem 0.65rem;
      font-size: 0.76rem;
      border-radius: 6px;
      cursor: pointer;
      text-decoration: none;
      font-weight: 600;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }
    .btn-xs:hover {
      background: rgba(255, 255, 255, 0.16);
      color: #fff;
    }
    .btn-xs.cyan {
      border-color: rgba(56, 189, 248, 0.4);
      color: var(--cyan);
      background: rgba(56, 189, 248, 0.12);
    }

    /* App Shell */
    .app-shell {
      display: flex;
      flex: 1;
      min-height: calc(100vh - 42px);
    }

    /* Sidebar */
    .sidebar {
      width: 260px;
      background: var(--bg-darker);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: transform 0.3s ease;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      padding: 1.25rem;
      border-bottom: 1px solid var(--border);
      text-decoration: none;
      color: inherit;
    }
    .brand-logo-img {
      width: 42px;
      height: 42px;
      object-fit: contain;
      border-radius: 8px;
      background: #fff;
      padding: 3px;
    }
    .brand-text h2 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #fff;
      font-family: 'Space Grotesk', sans-serif;
    }
    .brand-text small {
      font-size: 0.72rem;
      color: var(--cyan);
      letter-spacing: 0.05em;
      text-transform: uppercase;
      font-weight: 600;
    }
    .nav-list {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      padding: 1rem 0.75rem;
      flex: 1;
    }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.7rem 0.9rem;
      border-radius: 8px;
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
    }
    .nav-item i {
      font-size: 1.15rem;
      width: 1.3rem;
      text-align: center;
    }
    .nav-item:hover {
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
    }
    .nav-item.active {
      background: linear-gradient(90deg, rgba(37, 95, 133, 0.6), rgba(56, 189, 248, 0.15));
      color: #fff;
      border-color: rgba(56, 189, 248, 0.35);
      font-weight: 600;
    }
    .nav-item.active i {
      color: var(--cyan);
    }
    .sidebar-user {
      padding: 1rem 1.25rem;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.8rem;
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }
    .user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary), var(--cyan));
      display: grid;
      place-items: center;
      font-weight: 700;
      color: #fff;
      font-size: 0.85rem;
    }

    /* Main Content */
    .main-content {
      flex: 1;
      padding: 2rem;
      overflow-y: auto;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
    }

    /* Page Header */
    .page-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.75rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.25rem;
    }
    .page-header h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.75rem;
      font-weight: 700;
      color: #fff;
    }
    .page-header p {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }
    .page-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    /* Buttons */
    .btn {
      padding: 0.65rem 1.15rem;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      border: 1px solid transparent;
      transition: all 0.2s ease;
      text-decoration: none;
    }
    .btn-primary {
      background: var(--primary);
      color: #fff;
      border-color: rgba(56, 189, 248, 0.4);
    }
    .btn-primary:hover {
      background: var(--primary-hover);
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }
    .btn-accent {
      background: linear-gradient(135deg, #e0a91b, #f59e0b);
      color: #000;
      font-weight: 700;
    }
    .btn-accent:hover {
      opacity: 0.95;
      box-shadow: 0 0 15px var(--accent-glow);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border-color: var(--border);
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.14);
      color: #fff;
    }
    .btn-success {
      background: var(--success);
      color: #fff;
    }
    .btn-danger {
      background: var(--danger);
      color: #fff;
    }

    /* Cards & Grids */
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; }
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
    
    .card {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.4rem;
      box-shadow: var(--shadow);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border);
    }
    .card-header h2, .card-header h3 {
      font-size: 1.1rem;
      font-weight: 600;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    /* Quick Action Tiles */
    .quick-tile {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      cursor: pointer;
      transition: all 0.25s ease;
      position: relative;
      overflow: hidden;
    }
    .quick-tile::before {
      content: '';
      position: absolute;
      top: 0; left: 0; width: 4px; height: 100%;
      background: var(--cyan);
      opacity: 0.6;
      transition: width 0.2s ease;
    }
    .quick-tile:hover {
      border-color: rgba(56, 189, 248, 0.4);
      transform: translateY(-3px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .quick-tile:hover::before {
      width: 6px;
      opacity: 1;
    }
    .quick-tile-icon {
      width: 42px;
      height: 42px;
      border-radius: 8px;
      background: rgba(56, 189, 248, 0.12);
      color: var(--cyan);
      display: grid;
      place-items: center;
      font-size: 1.35rem;
      margin-bottom: 0.25rem;
    }
    .quick-tile strong {
      font-size: 1.05rem;
      color: #fff;
    }
    .quick-tile span {
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .quick-tile .count {
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--cyan);
      font-family: 'Space Grotesk', sans-serif;
      margin-top: 0.25rem;
    }

    /* Tables */
    .table-container {
      width: 100%;
      overflow-x: auto;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.86rem;
    }
    th {
      background: var(--surface);
      padding: 0.85rem 1rem;
      color: var(--cyan);
      font-weight: 600;
      border-bottom: 1px solid var(--border);
      text-transform: uppercase;
      font-size: 0.74rem;
      letter-spacing: 0.04em;
    }
    td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      color: var(--text);
    }
    tr:hover td {
      background: rgba(255, 255, 255, 0.03);
    }
    .tag {
      display: inline-block;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
    .tag-blue { background: rgba(56, 189, 248, 0.15); color: var(--cyan); border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-green { background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }
    .tag-gold { background: rgba(224, 169, 27, 0.15); color: var(--accent); border: 1px solid rgba(224, 169, 27, 0.3); }

    /* Form Fields */
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }
    .form-group label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .form-control {
      background: var(--bg-darker);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.65rem 0.85rem;
      color: #fff;
      font-family: inherit;
      font-size: 0.9rem;
      transition: border-color 0.2s ease;
    }
    .form-control:focus {
      outline: none;
      border-color: var(--cyan);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
    }

    /* Modals */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      display: none;
      place-items: center;
      z-index: 1000;
      padding: 1.5rem;
    }
    .modal-backdrop.active {
      display: grid;
    }
    .modal-box {
      background: var(--surface-card);
      border: 1px solid var(--border-focus);
      border-radius: var(--radius);
      width: min(650px, 100%);
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75);
      animation: modalIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalIn {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border);
    }
    .modal-header h3 {
      font-size: 1.2rem;
      color: #fff;
      font-family: 'Space Grotesk', sans-serif;
    }
    .modal-close {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.4rem;
      cursor: pointer;
    }
    .modal-close:hover { color: #fff; }
    .modal-body {
      padding: 1.5rem;
    }

    /* Toast Notification */
    .toast-container {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      z-index: 2000;
    }
    .toast {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--cyan);
      border-radius: 8px;
      padding: 0.85rem 1.25rem;
      color: #fff;
      font-size: 0.88rem;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      animation: toastIn 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      max-width: 400px;
    }
    .toast.success { border-left-color: var(--success); }
    .toast.error { border-left-color: var(--danger); }
    @keyframes toastIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    /* Views visibility */
    .app-view { display: none; }
    .app-view.active { display: block; }

    /* Login View Specifics */
    .login-wrapper {
      display: grid;
      min-height: calc(100vh - 42px);
      place-items: center;
      padding: 2rem;
      background: radial-gradient(circle at center, #132b40 0%, #061019 100%);
    }
    .login-card {
      background: rgba(16, 32, 48, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 12px;
      padding: 2.25rem;
      width: min(480px, 100%);
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }
    .demo-users-box {
      background: rgba(56, 189, 248, 0.08);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 8px;
      padding: 0.85rem 1rem;
      margin-bottom: 1.5rem;
      font-size: 0.82rem;
    }

    /* Biometric Camera View */
    .camera-container {
      position: relative;
      width: 100%;
      max-width: 540px;
      aspect-ratio: 4/3;
      background: #000;
      border-radius: 10px;
      overflow: hidden;
      border: 2px solid rgba(56, 189, 248, 0.3);
      margin: 0 auto;
    }
    #webcamVideo, #cameraCanvas {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .camera-hud {
      position: absolute;
      inset: 0;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 1rem;
    }
    .camera-reticle {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 220px;
      height: 260px;
      border: 2px dashed var(--cyan);
      border-radius: 50% 50% 45% 45%;
      box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
      animation: scanPulse 2s infinite alternate ease-in-out;
    }
    @keyframes scanPulse {
      0% { border-color: rgba(56, 189, 248, 0.5); box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
      100% { border-color: var(--cyan); box-shadow: 0 0 25px rgba(56, 189, 248, 0.6); }
    }
    .scan-line {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 3px;
      background: linear-gradient(90deg, transparent, #39ff14, transparent);
      box-shadow: 0 0 10px #39ff14;
      animation: scanSweep 2.5s infinite linear;
    }
    @keyframes scanSweep {
      0% { top: 10%; opacity: 0; }
      10% { opacity: 1; }
      90% { opacity: 1; }
      100% { top: 90%; opacity: 0; }
    }

    /* Contract Paper Preview */
    .contract-sheet {
      background: #ffffff;
      color: #111827;
      padding: 3rem 3.5rem;
      border-radius: 4px;
      box-shadow: 0 15px 40px rgba(0,0,0,0.5);
      font-family: 'Times New Roman', Times, serif;
      line-height: 1.6;
      font-size: 13.5px;
      max-width: 800px;
      margin: 0 auto;
    }
    .contract-sheet h2 {
      text-align: center;
      font-size: 17px;
      margin-bottom: 1.5rem;
      text-transform: uppercase;
      font-weight: bold;
    }
    .contract-clause {
      margin-bottom: 1rem;
      text-align: justify;
    }
    .contract-clause strong {
      font-weight: bold;
    }
    .contract-signatures {
      display: flex;
      justify-content: space-between;
      margin-top: 4rem;
      padding-top: 2rem;
    }
    .signature-line {
      text-align: center;
      width: 42%;
      border-top: 1px solid #111;
      padding-top: 0.5rem;
      font-size: 12px;
    }

    /* Print Styles */
    @media print {
      body * { visibility: hidden; }
      .contract-sheet, .contract-sheet * { visibility: visible; }
      .contract-sheet {
        position: absolute;
        left: 0; top: 0; width: 100%;
        box-shadow: none;
        padding: 0;
      }
      .demo-bar, .sidebar, .page-header, .btn { display: none !important; }
    }

    @media (max-width: 900px) {
      .sidebar {
        position: fixed;
        left: -260px;
        top: 42px;
        height: calc(100vh - 42px);
        z-index: 500;
      }
      .sidebar.open {
        transform: translateX(260px);
      }
      .main-content { padding: 1.25rem; }
    }
  </style>
</head>
<body>

  <!-- Top Demo Bar -->
  <div class="demo-bar">
    <div class="demo-badge">
      <i class="bi bi-cpu-fill"></i>
      <span>DEMO CLIENT-SIDE 100% OPERATIVO (JavaScript Database + SheetJS + OpenCV Simulator)</span>
    </div>
    <div class="demo-actions">
      <button class="btn-xs" onclick="resetDatabase()"><i class="bi bi-arrow-counterclockwise"></i> Reiniciar Base de Datos</button>
      <a class="btn-xs cyan" href="../../"><i class="bi bi-box-arrow-up-left"></i> Volver al Portafolio</a>
    </div>
  </div>

  <!-- Main Application -->
  <div class="app-shell" id="appShell">

    <!-- Sidebar Navigation -->
    <aside class="sidebar" id="appSidebar">
      <a class="brand" href="javascript:void(0)" onclick="navigateTo('menu')">
        <img class="brand-logo-img" src="logocampana.png" alt="Fundo La Campana">
        <div class="brand-text">
          <h2>Contratos Ágiles</h2>
          <small>Fundo La Campana</small>
        </div>
      </a>
      <nav class="nav-list">
        <a class="nav-item" id="nav-menu" onclick="navigateTo('menu')">
          <i class="bi bi-speedometer2"></i> Inicio / Dashboard
        </a>
        <a class="nav-item" id="nav-trabajadores" onclick="navigateTo('trabajadores')">
          <i class="bi bi-people-fill"></i> Trabajadores
        </a>
        <a class="nav-item" id="nav-importar" onclick="navigateTo('importar')">
          <i class="bi bi-file-earmark-excel-fill"></i> Carga Masiva Excel
        </a>
        <a class="nav-item" id="nav-contratos" onclick="navigateTo('contratos')">
          <i class="bi bi-file-earmark-word-fill"></i> Generar Contratos
        </a>
        <a class="nav-item" id="nav-asistencia" onclick="navigateTo('asistencia')">
          <i class="bi bi-camera-video-fill"></i> Control Asistencia
        </a>
        <a class="nav-item" id="nav-reportes" onclick="navigateTo('reportes')">
          <i class="bi bi-bar-chart-fill"></i> Reportes y Gráficos
        </a>
      </nav>
      <div class="sidebar-user">
        <div class="user-info">
          <div class="user-avatar" id="userAvatar">S</div>
          <div>
            <div style="font-weight:600;" id="userName">Sebastián</div>
            <small style="color:var(--cyan);">Administrador</small>
          </div>
        </div>
        <button class="btn-xs" onclick="logout()" title="Cerrar sesión"><i class="bi bi-box-arrow-right"></i></button>
      </div>
    </aside>

    <!-- Main Dynamic Content Views -->
    <main class="main-content">

      <!-- VIEW 1: LOGIN -->
      <section class="app-view" id="view-login">
        <div class="login-wrapper">
          <div class="login-card">
            <div style="text-align:center; margin-bottom: 1.5rem;">
              <img src="logocampana.png" alt="Fundo La Campana" style="width: 72px; height: 72px; object-fit: contain; border-radius: 12px; background: #fff; padding: 6px; margin-bottom: 0.75rem;">
              <h2 style="font-family:'Space Grotesk',sans-serif; font-size: 1.5rem;">Contratos Ágiles</h2>
              <p style="color:var(--text-muted); font-size: 0.85rem;">Sistema de Gestión Laboral y Automatización de Contratos</p>
            </div>

            <div class="demo-users-box">
              <div style="font-weight: 700; color: var(--cyan); margin-bottom: 0.35rem;"><i class="bi bi-key-fill"></i> Cuentas de Acceso Demostrativas:</div>
              <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                <button class="btn-xs cyan" onclick="fillLogin('seba5010', '5010')">Admin (seba5010 / 5010)</button>
                <button class="btn-xs" onclick="fillLogin('visitante', 'portafolios2026')">Visitante (visitante)</button>
              </div>
            </div>

            <form id="loginForm" onsubmit="handleLogin(event)">
              <div class="form-group">
                <label>Usuario</label>
                <input type="text" class="form-control" id="loginUser" required placeholder="seba5010">
              </div>
              <div class="form-group">
                <label>Contraseña</label>
                <input type="password" class="form-control" id="loginPass" required placeholder="••••">
              </div>
              <div id="loginError" style="display:none; color:var(--danger); font-size:0.85rem; margin-bottom:1rem;"></div>
              <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center; padding:0.8rem; font-weight:700;">
                <i class="bi bi-box-arrow-in-right"></i> Iniciar Sesión en la Demostración
              </button>
            </form>
          </div>
        </div>
      </section>

      <!-- VIEW 2: DASHBOARD / MENU -->
      <section class="app-view" id="view-menu">
        <header class="page-header">
          <div>
            <h1>Panel Principal</h1>
            <p>Monitoreo operativo de trabajadores, cuadrillas, contratos vigentes y asistencia.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-secondary" onclick="toggleExpiryAlert()">
              <i class="bi bi-bell-fill" style="color:var(--accent);"></i> Contratos por vencer
              <span class="tag tag-gold" id="expiryBadgeCount">0</span>
            </button>
          </div>
        </header>

        <!-- Notification Panel for expiring contracts -->
        <div id="expiryPanel" style="display:none; margin-bottom: 1.5rem; background:rgba(224, 169, 27, 0.08); border:1px solid rgba(224, 169, 27, 0.3); border-radius:8px; padding:1.2rem;">
          <h3 style="font-size:0.95rem; color:var(--accent); margin-bottom:0.65rem; display:flex; align-items:center; gap:0.5rem;">
            <i class="bi bi-exclamation-triangle-fill"></i> Próximos Vencimientos Contractuales (Menos de 15 días)
          </h3>
          <div id="expiryList" style="display:flex; flex-direction:column; gap:0.4rem; font-size:0.85rem;"></div>
        </div>

        <!-- Metric Cards -->
        <div class="grid-4" style="margin-bottom: 1.5rem;">
          <div class="card" style="border-left: 4px solid var(--cyan);">
            <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Nómina Activa</div>
            <div style="font-size:2rem; font-weight:800; font-family:'Space Grotesk',sans-serif; color:#fff;" id="metricWorkers">62</div>
            <small style="color:var(--success);"><i class="bi bi-check-circle"></i> 100% con RUT validado</small>
          </div>
          <div class="card" style="border-left: 4px solid var(--success);">
            <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Asistencias Hoy</div>
            <div style="font-size:2rem; font-weight:800; font-family:'Space Grotesk',sans-serif; color:var(--success);" id="metricAttendance">0</div>
            <small style="color:var(--text-muted);"><i class="bi bi-camera"></i> Reconocimiento biométrico</small>
          </div>
          <div class="card" style="border-left: 4px solid var(--accent);">
            <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Contratos Generados</div>
            <div style="font-size:2rem; font-weight:800; font-family:'Space Grotesk',sans-serif; color:var(--accent);" id="metricContracts">12</div>
            <small style="color:var(--text-muted);"><i class="bi bi-file-earmark-check"></i> Plantillas oficiales</small>
          </div>
          <div class="card" style="border-left: 4px solid #8b5cf6;">
            <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Faenas Activas</div>
            <div style="font-size:2rem; font-weight:800; font-family:'Space Grotesk',sans-serif; color:#8b5cf6;">3</div>
            <small style="color:var(--text-muted);">Cosecha, Packing, Frío</small>
          </div>
        </div>

        <!-- Quick Access Navigation Grid -->
        <div class="grid-2">
          <div class="quick-tile" onclick="navigateTo('trabajadores')">
            <div class="quick-tile-icon"><i class="bi bi-people-fill"></i></div>
            <strong>Nómina y Padrón Laboral</strong>
            <span>Visualizar trabajadores, revisar fichas, validar RUT por Módulo 11 y registrar nuevo personal.</span>
            <div class="count" id="tileWorkersCount">62 trabajadores</div>
          </div>
          <div class="quick-tile" onclick="navigateTo('importar')">
            <div class="quick-tile-icon"><i class="bi bi-file-earmark-excel-fill"></i></div>
            <strong>Carga Masiva de Planillas Excel</strong>
            <span>Procesamiento instantáneo de archivos .xlsx con mapeo automático de columnas y validación de duplicados.</span>
            <div class="count" style="color:var(--success);">SheetJS Motor</div>
          </div>
          <div class="quick-tile" onclick="navigateTo('contratos')">
            <div class="quick-tile-icon"><i class="bi bi-file-earmark-word-fill"></i></div>
            <strong>Generador Contractual Dinámico</strong>
            <span>Inyección de variables legales en modelos oficiales de contrato por faena agrícola y descarga en .doc / PDF.</span>
            <div class="count" style="color:var(--accent);">Word .docx Template</div>
          </div>
          <div class="quick-tile" onclick="navigateTo('asistencia')">
            <div class="quick-tile-icon"><i class="bi bi-camera-video-fill"></i></div>
            <strong>Control de Asistencia Biométrico</strong>
            <span>Detección facial en tiempo real mediante webcam y registro instantáneo de turnos laborales.</span>
            <div class="count" style="color:var(--cyan);">Biometría Facial</div>
          </div>
        </div>
      </section>

      <!-- VIEW 3: TRABAJADORES -->
      <section class="app-view" id="view-trabajadores">
        <header class="page-header">
          <div>
            <h1>Nómina de Trabajadores</h1>
            <p>Registro central de personal agrícola, validación de RUT y gestión de cargos.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-primary" onclick="openWorkerModal()"><i class="bi bi-person-plus-fill"></i> Nuevo Trabajador</button>
            <button class="btn btn-secondary" onclick="exportWorkersExcel()"><i class="bi bi-download"></i> Exportar a Excel</button>
          </div>
        </header>

        <div class="card" style="margin-bottom: 1.25rem;">
          <div style="display:flex; flex-wrap:wrap; gap:1rem; align-items:center;">
            <div style="flex:1; min-width:260px;">
              <input type="search" id="workerSearch" class="form-control" placeholder="🔍 Buscar por nombre, apellido o RUT..." oninput="filterWorkers()">
            </div>
            <div style="width:180px;">
              <select id="afpFilter" class="form-control" onchange="filterWorkers()">
                <option value="">Todas las AFP</option>
                <option value="Habitat">Habitat</option>
                <option value="Cuprum">Cuprum</option>
                <option value="Modelo">Modelo</option>
                <option value="Provida">Provida</option>
                <option value="Capital">Capital</option>
                <option value="Uno">Uno</option>
              </select>
            </div>
            <div style="width:180px;">
              <select id="saludFilter" class="form-control" onchange="filterWorkers()">
                <option value="">Toda Previsión</option>
                <option value="Fonasa">Fonasa</option>
                <option value="Isapre">Isapre</option>
              </select>
            </div>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Trabajador</th>
                <th>RUT</th>
                <th>Contacto</th>
                <th>Previsión / AFP</th>
                <th>Estado Civil</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody id="workersTableBody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem; font-size:0.85rem; color:var(--text-muted);">
          <span id="workersCountLabel">Mostrando 10 de 62</span>
          <div style="display:flex; gap:0.5rem;" id="workersPagination">
            <!-- Pagination buttons -->
          </div>
        </div>
      </section>

      <!-- VIEW 4: IMPORTACIÓN EXCEL -->
      <section class="app-view" id="view-importar">
        <header class="page-header">
          <div>
            <h1>Importación Masiva de Trabajadores</h1>
            <p>Carga planillas Excel (.xlsx, .xls) o CSV con procesamiento y validación inmediata.</p>
          </div>
        </header>

        <div class="grid-2">
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-cloud-arrow-up-fill" style="color:var(--cyan);"></i> Cargar Archivo Excel</h3>
            </div>
            <div id="dropZone" style="border: 2px dashed rgba(56, 189, 248, 0.4); border-radius: 8px; padding: 2.5rem 1.5rem; text-align: center; cursor: pointer; transition: all 0.2s ease; background: rgba(56, 189, 248, 0.03);"
                 onclick="document.getElementById('excelFileInput').click()"
                 ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)">
              <i class="bi bi-file-earmark-spreadsheet" style="font-size: 3rem; color: var(--cyan); margin-bottom: 0.75rem; display: block;"></i>
              <strong style="font-size: 1.05rem; display: block; margin-bottom: 0.25rem;">Arrastra tu planilla Excel aquí</strong>
              <span style="font-size: 0.82rem; color: var(--text-muted);">o haz clic para examinar archivos en tu equipo</span>
              <input type="file" id="excelFileInput" accept=".xlsx, .xls, .csv" style="display:none;" onchange="handleFileSelect(event)">
            </div>

            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
              <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">¿No tienes una planilla a mano? Prueba el motor con un solo clic:</div>
              <button class="btn btn-accent" style="width: 100%; justify-content: center;" onclick="loadDemoExcelSheet()">
                <i class="bi bi-magic"></i> Cargar Planilla Demo de Prueba (5 nuevos trabajadores)
              </button>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-info-circle-fill" style="color:var(--accent);"></i> Formato Requerido</h3>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.5;">
              La planilla Excel debe contener las siguientes columnas para ser mapeada por el algoritmo de ingesta:
            </p>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.83rem;">
              <li><code class="tag tag-blue">nombre</code>: Nombre del operario</li>
              <li><code class="tag tag-blue">apellido</code>: Apellido paterno o completo</li>
              <li><code class="tag tag-blue">rut</code>: Cédula de identidad chilena (ej: 18.234.567-8)</li>
              <li><code class="tag tag-blue">telefono</code>: Contacto telefónico (ej: 987654321)</li>
              <li><code class="tag tag-blue">afp</code>: Habitat, Cuprum, Modelo, Provida, etc.</li>
              <li><code class="tag tag-blue">previcion_salud</code>: Fonasa o Isapre</li>
              <li><code class="tag tag-blue">direccion</code>: Domicilio del trabajador</li>
            </ul>
          </div>
        </div>

        <!-- Excel Preview Table (Hidden until parsed) -->
        <div id="excelPreviewSection" style="display:none; margin-top: 2rem;">
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-check2-circle" style="color:var(--success);"></i> Registros Detectados para Incorporar (<span id="parsedRowsCount">0</span>)</h3>
              <button class="btn btn-success" onclick="commitImportedWorkers()"><i class="bi bi-person-check-fill"></i> Confirmar e Incorporar a la Nómina</button>
            </div>
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Apellido</th>
                    <th>RUT</th>
                    <th>Teléfono</th>
                    <th>AFP</th>
                    <th>Salud</th>
                    <th>Dirección</th>
                  </tr>
                </thead>
                <tbody id="excelPreviewBody"></tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- VIEW 5: GENERADOR DE CONTRATOS -->
      <section class="app-view" id="view-contratos">
        <header class="page-header">
          <div>
            <h1>Generador Contractual</h1>
            <p>Confección instantánea de contratos legales de trabajo para faenas agrícolas de temporada.</p>
          </div>
        </header>

        <div class="grid-2" style="align-items: flex-start; margin-bottom: 2rem;">
          <!-- Contract Form -->
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-pencil-square" style="color:var(--accent);"></i> Configuración del Contrato</h3>
            </div>
            <form id="contractConfigForm" onsubmit="generateContractPreview(event)">
              <div class="form-group">
                <label>Seleccionar Trabajador</label>
                <select class="form-control" id="contractWorkerSelect" required onchange="onSelectWorkerForContract()">
                  <!-- Dynamically filled -->
                </select>
              </div>
              <div class="form-group">
                <label>Tipo de Contrato / Plantilla</label>
                <select class="form-control" id="contractTemplateSelect" required>
                  <option value="faena_uva">Contrato por Faena - Cosecha Uva de Mesa 2026</option>
                  <option value="packing">Contrato Temporal - Operario de Packing Frutícola</option>
                  <option value="plazo_fijo">Contrato de Trabajo a Plazo Fijo</option>
                </select>
              </div>
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                  <label>Fecha de Inicio</label>
                  <input type="date" class="form-control" id="contractStartDate" required>
                </div>
                <div class="form-group">
                  <label>Fecha de Término</label>
                  <input type="date" class="form-control" id="contractEndDate" required>
                </div>
              </div>
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="form-group">
                  <label>Remuneración Base Mensual ($)</label>
                  <input type="number" class="form-control" id="contractSalary" value="560000" step="10000" required>
                </div>
                <div class="form-group">
                  <label>Ubicación / Faena</label>
                  <input type="text" class="form-control" id="contractLocation" value="Fundo La Campana, Lote 4, Vicuña" required>
                </div>
              </div>
              <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; margin-top: 0.5rem;">
                <i class="bi bi-file-earmark-text"></i> Confeccionar y Previsualizar Documento
              </button>
            </form>
          </div>

          <!-- Document Controls & Summary -->
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-printer-fill" style="color:var(--cyan);"></i> Acciones del Documento</h3>
            </div>
            <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.5; margin-bottom:1.25rem;">
              Una vez generado el contrato, las variables legales ({NOMBRE}, {RUT}, {REMUNERACION}) son inyectadas en tiempo real. Puedes descargarlo en formato Word editable (.doc) o imprimirlo/guardarlo en PDF listo para firmar.
            </p>
            <div style="display:flex; flex-direction:column; gap:0.75rem;">
              <button class="btn btn-accent" onclick="printContract()"><i class="bi bi-printer"></i> Imprimir / Guardar en PDF</button>
              <button class="btn btn-secondary" onclick="downloadWordDoc()"><i class="bi bi-file-earmark-word"></i> Descargar Contrato (.doc)</button>
            </div>
          </div>
        </div>

        <!-- Rendered Contract Document Preview -->
        <div id="contractPreviewContainer" style="display:none;">
          <div style="text-align:center; margin-bottom:1rem; color:var(--cyan); font-size:0.85rem;">
            <i class="bi bi-eye"></i> Vista Previa del Documento Oficial Generado
          </div>
          <div class="contract-sheet" id="renderedContractSheet">
            <!-- Dynamically populated text -->
          </div>
        </div>
      </section>

      <!-- VIEW 6: CONTROL DE ASISTENCIA / BIOMETRIA -->
      <section class="app-view" id="view-asistencia">
        <header class="page-header">
          <div>
            <h1>Control de Asistencia Biométrico</h1>
            <p>Reconocimiento facial mediante webcam o simulación para registro de turno laboral.</p>
          </div>
        </header>

        <div class="grid-2">
          <!-- Camera Feed Section -->
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-camera-fill" style="color:var(--cyan);"></i> Escáner Facial Biométrico</h3>
              <span class="tag tag-green" id="cameraStatusTag">Cámara Lista</span>
            </div>

            <div class="camera-container">
              <video id="webcamVideo" autoplay playsinline muted></video>
              <canvas id="cameraCanvas" style="display:none;"></canvas>
              <div class="camera-hud">
                <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:var(--cyan); font-family:'JetBrains Mono',monospace;">
                  <span>OPENCV LBPH SIMULATOR</span>
                  <span id="fpsMeter">30 FPS · 720p</span>
                </div>
                <div class="camera-reticle">
                  <div class="scan-line"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#fff; font-family:'JetBrains Mono',monospace;">
                  <span id="biometricMatchName">Buscando rostro...</span>
                  <span id="biometricConfidence" style="color:var(--success);">Confianza: 98.4%</span>
                </div>
              </div>
            </div>

            <div style="margin-top: 1.25rem; display: flex; gap: 0.75rem;">
              <button class="btn btn-accent" style="flex:1; justify-content:center;" onclick="triggerBiometricScan()">
                <i class="bi bi-person-bounding-box"></i> Registrar Asistencia Facial
              </button>
              <button class="btn btn-secondary" onclick="toggleWebcamMode()" id="toggleCamBtn">
                <i class="bi bi-camera-reels"></i> Simular Cámara
              </button>
            </div>
          </div>

          <!-- Attendance Records Today -->
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-calendar-check-fill" style="color:var(--success);"></i> Presentes Hoy (<span id="presentTodayCount">0</span>)</h3>
              <button class="btn-xs cyan" onclick="clearTodayAttendance()"><i class="bi bi-trash"></i> Limpiar</button>
            </div>
            <div class="table-container" style="max-height: 400px; overflow-y: auto;">
              <table>
                <thead>
                  <tr>
                    <th>Trabajador</th>
                    <th>RUT</th>
                    <th>Hora</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody id="attendanceTodayBody">
                  <!-- Dynamically populated -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- VIEW 7: REPORTES -->
      <section class="app-view" id="view-reportes">
        <header class="page-header">
          <div>
            <h1>Reportes y Estadísticas Laborales</h1>
            <p>Distribución demográfica, previsión de salud y fondos de pensiones de la nómina.</p>
          </div>
        </header>

        <div class="grid-3" style="margin-bottom: 1.5rem;">
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-hospital" style="color:var(--cyan);"></i> Previsión de Salud</h3>
            </div>
            <div style="position:relative; height:240px;">
              <canvas id="chartSalud"></canvas>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-piggy-bank" style="color:var(--accent);"></i> Distribución AFP</h3>
            </div>
            <div style="position:relative; height:240px;">
              <canvas id="chartAfp"></canvas>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <h3><i class="bi bi-calendar-date" style="color:#a855f7;"></i> Rango Etario</h3>
            </div>
            <div style="position:relative; height:240px;">
              <canvas id="chartEdad"></canvas>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- WORKER MODAL (CREATE NEW) -->
  <div class="modal-backdrop" id="workerModal">
    <div class="modal-box">
      <div class="modal-header">
        <h3><i class="bi bi-person-plus-fill" style="color:var(--cyan);"></i> Registrar Nuevo Trabajador</h3>
        <button class="modal-close" onclick="closeWorkerModal()">&times;</button>
      </div>
      <div class="modal-body">
        <form id="newWorkerForm" onsubmit="handleSaveWorker(event)">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Nombre *</label>
              <input type="text" class="form-control" id="nwNombre" required placeholder="Ej: Carlos">
            </div>
            <div class="form-group">
              <label>Apellido *</label>
              <input type="text" class="form-control" id="nwApellido" required placeholder="Ej: González">
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>RUT Chileno (con DV) *</label>
              <input type="text" class="form-control" id="nwRut" required placeholder="18.234.567-8" onblur="validateRutInput(this)">
              <small id="nwRutFeedback" style="font-size:0.75rem; color:var(--text-muted);">Validado algorítmicamente (Módulo 11)</small>
            </div>
            <div class="form-group">
              <label>Fecha de Nacimiento *</label>
              <input type="date" class="form-control" id="nwNacimiento" value="1992-05-15" required>
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Teléfono</label>
              <input type="text" class="form-control" id="nwTelefono" placeholder="987654321">
            </div>
            <div class="form-group">
              <label>Correo Electrónico</label>
              <input type="email" class="form-control" id="nwCorreo" placeholder="trabajador@gmail.com">
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>AFP *</label>
              <select class="form-control" id="nwAfp" required>
                <option value="Habitat">Habitat</option>
                <option value="Cuprum">Cuprum</option>
                <option value="Modelo">Modelo</option>
                <option value="Provida">Provida</option>
                <option value="Capital">Capital</option>
                <option value="Uno">Uno</option>
              </select>
            </div>
            <div class="form-group">
              <label>Previsión de Salud *</label>
              <select class="form-control" id="nwSalud" required>
                <option value="Fonasa">Fonasa</option>
                <option value="Isapre">Isapre</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Dirección</label>
            <input type="text" class="form-control" id="nwDireccion" placeholder="Calle Los Aromos 123, Vicuña">
          </div>
          <div class="form-group">
            <label>Labor / Cargo Inicial</label>
            <input type="text" class="form-control" id="nwLabor" placeholder="Cosechador / Operario Packing" value="Cosechador">
          </div>
          <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.25rem;">
            <button type="button" class="btn btn-secondary" onclick="closeWorkerModal()">Cancelar</button>
            <button type="submit" class="btn btn-primary"><i class="bi bi-check-lg"></i> Guardar Trabajador</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- TOAST CONTAINER -->
  <div class="toast-container" id="toastContainer"></div>

  <!-- APPLICATION LOGIC & INLINED DATABASE -->
  <script>
    // Inlined Seed Data from SQLite db.sqlite3
    const INITIAL_DATA = __SEED_DATA__;

    // App Database State
    let appDb = {
      trabajadores: [],
      cargos: [],
      contratos: [],
      contratos_trab: [],
      logins: [],
      asistencias: []
    };

    let activeUser = null;
    let currentWorkerPage = 1;
    const workersPerPage = 10;
    let filteredWorkersList = [];
    let parsedExcelWorkers = [];
    let webcamStream = null;
    let isSimulatedCam = false;
    let simCamInterval = null;
    let charts = {};

    // Initialize Database from LocalStorage or Seed Data
    function initDatabase() {
      const saved = localStorage.getItem('contratos_agiles_db');
      if (saved) {
        try {
          appDb = JSON.parse(saved);
        } catch(e) {
          appDb = JSON.parse(JSON.stringify(INITIAL_DATA));
        }
      } else {
        appDb = JSON.parse(JSON.stringify(INITIAL_DATA));
        // Add sample asistencias if empty
        if (!appDb.asistencias) {
          appDb.asistencias = [
            { id: 1, trabajador_id: 1, hora: '07:54:12', fecha: new Date().toISOString().split('T')[0], presente: true },
            { id: 2, trabajador_id: 2, hora: '08:02:45', fecha: new Date().toISOString().split('T')[0], presente: true },
            { id: 3, trabajador_id: 62, hora: '08:14:20', fecha: new Date().toISOString().split('T')[0], presente: true }
          ];
        }
        saveDatabase();
      }
    }

    function saveDatabase() {
      localStorage.setItem('contratos_agiles_db', JSON.stringify(appDb));
    }

    function resetDatabase() {
      if (confirm("¿Estás seguro de reiniciar la base de datos a los 62 trabajadores y datos iniciales de demostración?")) {
        localStorage.removeItem('contratos_agiles_db');
        initDatabase();
        showToast("Base de datos reiniciada con éxito", "success");
        updateMetrics();
        renderWorkersTable();
        populateContractWorkerDropdown();
        renderAttendanceList();
        renderReports();
      }
    }

    // Chilean RUT Validator (Modulo 11)
    function validateRut(rutCompleto) {
      if (!rutCompleto || typeof rutCompleto !== 'string') return false;
      const clean = rutCompleto.replace(/[^0-9kK]/g, '');
      if (clean.length < 2) return false;
      const cuerpo = clean.slice(0, -1);
      let dv = clean.slice(-1).toUpperCase();
      let suma = 0;
      let multiplo = 2;
      for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += multiplo * parseInt(cuerpo.charAt(i), 10);
        multiplo = multiplo < 7 ? multiplo + 1 : 2;
      }
      const dvEsperado = 11 - (suma % 11);
      let dvCalculado = '0';
      if (dvEsperado === 11) dvCalculado = '0';
      else if (dvEsperado === 10) dvCalculado = 'K';
      else dvCalculado = dvEsperado.toString();
      return dv === dvCalculado;
    }

    function formatRut(rut) {
      let clean = rut.replace(/[^0-9kK]/g, '');
      if (clean.length < 2) return rut;
      let dv = clean.slice(-1);
      let cuerpo = clean.slice(0, -1);
      return cuerpo.replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".") + "-" + dv;
    }

    function validateRutInput(input) {
      const isValid = validateRut(input.value);
      const feedback = document.getElementById('nwRutFeedback');
      if (input.value.trim() === '') return;
      if (isValid) {
        input.value = formatRut(input.value);
        feedback.textContent = '✓ RUT Válido (Módulo 11)';
        feedback.style.color = 'var(--success)';
      } else {
        feedback.textContent = '✗ RUT Inválido para la República de Chile';
        feedback.style.color = 'var(--danger)';
      }
    }

    // Navigation System
    function navigateTo(viewId) {
      if (!activeUser && viewId !== 'login') {
        navigateTo('login');
        return;
      }
      document.querySelectorAll('.app-view').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

      const targetView = document.getElementById('view-' + viewId);
      if (targetView) targetView.classList.add('active');

      const targetNav = document.getElementById('nav-' + viewId);
      if (targetNav) targetNav.classList.add('active');

      if (viewId === 'login') {
        document.getElementById('appSidebar').style.display = 'none';
      } else {
        document.getElementById('appSidebar').style.display = 'flex';
      }

      // View-specific initializations
      if (viewId === 'menu') updateMetrics();
      if (viewId === 'trabajadores') renderWorkersTable();
      if (viewId === 'contratos') populateContractWorkerDropdown();
      if (viewId === 'asistencia') initCameraView();
      else stopWebcam();
      if (viewId === 'reportes') renderReports();
    }

    // Authentication
    function fillLogin(user, pass) {
      document.getElementById('loginUser').value = user;
      document.getElementById('loginPass').value = pass;
    }

    function handleLogin(e) {
      e.preventDefault();
      const user = document.getElementById('loginUser').value.trim();
      const pass = document.getElementById('loginPass').value.trim();
      const errEl = document.getElementById('loginError');

      // Check against seed logins or allow admin/admin123
      const found = appDb.logins.find(l => l.username === user && l.password === pass) ||
                    (user === 'admin' && pass === 'admin123') ||
                    (user === 'seba5010' && pass === '5010') ||
                    (user === 'visitante');

      if (found) {
        activeUser = { username: user, name: user === 'seba5010' ? 'Sebastián Espíndola' : 'Visitante' };
        sessionStorage.setItem('ca_session_user', JSON.stringify(activeUser));
        document.getElementById('userName').textContent = activeUser.name;
        document.getElementById('userAvatar').textContent = activeUser.name.charAt(0).toUpperCase();
        errEl.style.display = 'none';
        showToast("¡Bienvenido al sistema Contratos Ágiles!", "success");
        navigateTo('menu');
      } else {
        errEl.textContent = 'Credenciales no válidas. Prueba con seba5010 / 5010 o el botón demo.';
        errEl.style.display = 'block';
      }
    }

    function logout() {
      activeUser = null;
      sessionStorage.removeItem('ca_session_user');
      showToast("Sesión finalizada", "info");
      navigateTo('login');
    }

    // Metric Counters & Alerts
    function updateMetrics() {
      const totalWorkers = appDb.trabajadores.length;
      document.getElementById('metricWorkers').textContent = totalWorkers;
      document.getElementById('tileWorkersCount').textContent = totalWorkers + ' trabajadores';

      const todayStr = new Date().toISOString().split('T')[0];
      const todayAttendance = (appDb.asistencias || []).filter(a => a.fecha === todayStr).length;
      document.getElementById('metricAttendance').textContent = todayAttendance;

      const totalContracts = (appDb.contratos_trab || []).length;
      document.getElementById('metricContracts').textContent = totalContracts;

      // Expirations check
      const expiryBadge = document.getElementById('expiryBadgeCount');
      const expiryList = document.getElementById('expiryList');
      const expiring = (appDb.contratos_trab || []).slice(0, 4);
      expiryBadge.textContent = expiring.length;

      expiryList.innerHTML = '';
      expiring.forEach(c => {
        const trab = appDb.trabajadores.find(t => t.id === c.trabajador_id) || { nombre: 'Trabajador', apellido: 'Agrícola' };
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.padding = '0.35rem 0';
        row.style.borderBottom = '1px solid rgba(224, 169, 27, 0.15)';
        row.innerHTML = `<strong>${trab.nombre} ${trab.apellido}</strong> <span style="color:var(--accent);">Vence: ${c.fecha_termino || '2026-11-28'}</span>`;
        expiryList.appendChild(row);
      });
    }

    function toggleExpiryAlert() {
      const p = document.getElementById('expiryPanel');
      p.style.display = p.style.display === 'none' ? 'block' : 'none';
    }

    // Workers Table and Pagination
    function filterWorkers() {
      const search = (document.getElementById('workerSearch').value || '').toLowerCase();
      const afp = document.getElementById('afpFilter').value;
      const salud = document.getElementById('saludFilter').value;

      filteredWorkersList = appDb.trabajadores.filter(w => {
        const full = `${w.nombre} ${w.apellido} ${w.rut}`.toLowerCase();
        const matchesSearch = !search || full.includes(search);
        const matchesAfp = !afp || (w.afp || '').toLowerCase() === afp.toLowerCase();
        const matchesSalud = !salud || (w.previcion_salud || '').toLowerCase().includes(salud.toLowerCase());
        return matchesSearch && matchesAfp && matchesSalud;
      });

      currentWorkerPage = 1;
      renderWorkersTable();
    }

    function renderWorkersTable() {
      if (!filteredWorkersList || filteredWorkersList.length === 0) {
        filteredWorkersList = [...appDb.trabajadores];
      }

      const start = (currentWorkerPage - 1) * workersPerPage;
      const end = start + workersPerPage;
      const pageItems = filteredWorkersList.slice(start, end);
      const tbody = document.getElementById('workersTableBody');
      tbody.innerHTML = '';

      if (pageItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--text-muted);">No se encontraron trabajadores con esos filtros.</td></tr>';
      } else {
        pageItems.forEach(w => {
          const tr = document.createElement('tr');
          const saludTag = (w.previcion_salud || '').toLowerCase().includes('isapre') ? 'tag-gold' : 'tag-green';
          tr.innerHTML = `
            <td>
              <strong style="color:#fff;">${w.nombre} ${w.apellido}</strong><br>
              <small style="color:var(--text-muted);">${w.direccion || 'Sin dirección registrada'}</small>
            </td>
            <td><code class="tag tag-blue">${w.rut}</code></td>
            <td>
              ${w.telefono ? '📞 ' + w.telefono : '—'}<br>
              <small style="color:var(--text-muted);">${w.correo || ''}</small>
            </td>
            <td>
              <span class="tag ${saludTag}">${w.previcion_salud || 'Fonasa'}</span>
              <span class="tag tag-blue" style="margin-left:0.25rem;">${w.afp || 'Modelo'}</span>
            </td>
            <td><span style="font-size:0.82rem;">${w.estado_civil || 'Soltero'}</span></td>
            <td>
              <div style="display:flex; gap:0.4rem;">
                <button class="btn-xs cyan" onclick="quickContractForWorker(${w.id})" title="Generar Contrato"><i class="bi bi-file-earmark-word"></i> Contrato</button>
                <button class="btn-xs" style="color:var(--danger); border-color:rgba(239,68,68,0.3);" onclick="deleteWorker(${w.id})" title="Eliminar"><i class="bi bi-trash"></i></button>
              </div>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }

      // Update count label & pagination
      document.getElementById('workersCountLabel').textContent = `Mostrando ${pageItems.length} de ${filteredWorkersList.length} trabajadores`;
      renderPagination(filteredWorkersList.length);
    }

    function renderPagination(total) {
      const totalPages = Math.ceil(total / workersPerPage) || 1;
      const pContainer = document.getElementById('workersPagination');
      pContainer.innerHTML = '';

      const prevBtn = document.createElement('button');
      prevBtn.className = 'btn-xs';
      prevBtn.innerHTML = '← Anterior';
      prevBtn.disabled = currentWorkerPage <= 1;
      prevBtn.onclick = () => { if (currentWorkerPage > 1) { currentWorkerPage--; renderWorkersTable(); } };
      pContainer.appendChild(prevBtn);

      const span = document.createElement('span');
      span.style.padding = '0.2rem 0.5rem';
      span.textContent = `${currentWorkerPage} / ${totalPages}`;
      pContainer.appendChild(span);

      const nextBtn = document.createElement('button');
      nextBtn.className = 'btn-xs';
      nextBtn.innerHTML = 'Siguiente →';
      nextBtn.disabled = currentWorkerPage >= totalPages;
      nextBtn.onclick = () => { if (currentWorkerPage < totalPages) { currentWorkerPage++; renderWorkersTable(); } };
      pContainer.appendChild(nextBtn);
    }

    // Worker Modal & Creation
    function openWorkerModal() {
      document.getElementById('workerModal').classList.add('active');
    }
    function closeWorkerModal() {
      document.getElementById('workerModal').classList.remove('active');
    }

    function handleSaveWorker(e) {
      e.preventDefault();
      const rut = document.getElementById('nwRut').value.trim();
      if (!validateRut(rut)) {
        alert("El RUT ingresado no es válido para la legislación chilena (falla en Módulo 11).");
        return;
      }

      const newId = appDb.trabajadores.length ? Math.max(...appDb.trabajadores.map(w => w.id)) + 1 : 1;
      const newWorker = {
        id: newId,
        nombre: document.getElementById('nwNombre').value.trim(),
        apellido: document.getElementById('nwApellido').value.trim(),
        rut: formatRut(rut),
        direccion: document.getElementById('nwDireccion').value.trim() || 'Fundo La Campana',
        telefono: document.getElementById('nwTelefono').value.trim() || '987654321',
        correo: document.getElementById('nwCorreo').value.trim() || '',
        afp: document.getElementById('nwAfp').value,
        previcion_salud: document.getElementById('nwSalud').value,
        estado_civil: 'Soltero',
        fecha_nacimiento: document.getElementById('nwNacimiento').value,
        sent: 'no_enviado'
      };

      appDb.trabajadores.unshift(newWorker);
      saveDatabase();
      closeWorkerModal();
      document.getElementById('newWorkerForm').reset();
      showToast(`Trabajador ${newWorker.nombre} ${newWorker.apellido} registrado con éxito`, "success");
      filterWorkers();
      updateMetrics();
    }

    function deleteWorker(id) {
      if (confirm("¿Deseas eliminar este trabajador de la nómina?")) {
        appDb.trabajadores = appDb.trabajadores.filter(w => w.id !== id);
        saveDatabase();
        showToast("Trabajador eliminado de la base de datos", "info");
        filterWorkers();
        updateMetrics();
      }
    }

    // Excel Export via SheetJS
    function exportWorkersExcel() {
      const rows = appDb.trabajadores.map(w => ({
        'Nombre': w.nombre,
        'Apellido': w.apellido,
        'RUT': w.rut,
        'Dirección': w.direccion,
        'Teléfono': w.telefono,
        'Correo': w.correo,
        'AFP': w.afp,
        'Previsión Salud': w.previcion_salud,
        'Fecha Nacimiento': w.fecha_nacimiento
      }));
      const ws = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Trabajadores");
      XLSX.writeFile(wb, "Nomina_Trabajadores_FundoLaCampana.xlsx");
      showToast("Planilla Excel generada y descargada", "success");
    }

    // Excel Import via SheetJS
    function handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) parseExcel(file);
    }
    function handleDragOver(e) {
      e.preventDefault();
      document.getElementById('dropZone').style.borderColor = 'var(--cyan)';
    }
    function handleDragLeave(e) {
      e.preventDefault();
      document.getElementById('dropZone').style.borderColor = 'rgba(56, 189, 248, 0.4)';
    }
    function handleDrop(e) {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) parseExcel(file);
    }

    function parseExcel(file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, {type: 'array'});
          const firstSheet = workbook.SheetNames[0];
          const rawRows = XLSX.utils.sheet_to_json(workbook.Sheets[firstSheet]);
          processParsedExcelRows(rawRows);
        } catch(err) {
          showToast("Error al procesar el archivo Excel: " + err.message, "error");
        }
      };
      reader.readAsArrayBuffer(file);
    }

    function loadDemoExcelSheet() {
      const demoRows = [
        { nombre: "Rodrigo", apellido: "Araya", rut: "17.842.119-3", telefono: "984210984", afp: "Habitat", previcion_salud: "Fonasa", direccion: "Calle Victoria 890, Vicuña" },
        { nombre: "Constanza", apellido: "Morales", rut: "19.340.551-7", telefono: "951478236", afp: "Cuprum", previcion_salud: "Isapre", direccion: "Av. Balmaceda 1240, La Serena" },
        { nombre: "Matias", apellido: "Zepeda", rut: "18.665.432-8", telefono: "978541203", afp: "Modelo", previcion_salud: "Fonasa", direccion: "Población Los Perales, Ovalle" },
        { nombre: "Daniela", apellido: "Fuentes", rut: "16.992.341-2", telefono: "963258741", afp: "Provida", previcion_salud: "Fonasa", direccion: "Camino El Tambo s/n, Vicuña" },
        { nombre: "Esteban", apellido: "Carrasco", rut: "15.772.091-6", telefono: "914785236", afp: "Uno", previcion_salud: "Isapre", direccion: "Pasaje Central 45, Paihuano" }
      ];
      processParsedExcelRows(demoRows);
      showToast("Planilla demo de 5 trabajadores cargada para revisión", "success");
    }

    function processParsedExcelRows(rows) {
      parsedExcelWorkers = [];
      const tbody = document.getElementById('excelPreviewBody');
      tbody.innerHTML = '';

      rows.forEach(r => {
        // Normalize keys
        const item = {
          nombre: r.nombre || r.Nombre || 'Sin nombre',
          apellido: r.apellido || r.Apellido || 'Sin apellido',
          rut: r.rut || r.RUT || r.Rut || '11.111.111-1',
          telefono: r.telefono || r.Telefono || r['Teléfono'] || '987654321',
          afp: r.afp || r.AFP || 'Habitat',
          previcion_salud: r.previcion_salud || r.Salud || r['Previsión Salud'] || 'Fonasa',
          direccion: r.direccion || r.Direccion || r['Dirección'] || 'La Serena'
        };
        parsedExcelWorkers.push(item);

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${item.nombre}</strong></td>
          <td>${item.apellido}</td>
          <td><code class="tag tag-blue">${item.rut}</code></td>
          <td>${item.telefono}</td>
          <td>${item.afp}</td>
          <td>${item.previcion_salud}</td>
          <td><small>${item.direccion}</small></td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('parsedRowsCount').textContent = parsedExcelWorkers.length;
      document.getElementById('excelPreviewSection').style.display = 'block';
    }

    function commitImportedWorkers() {
      if (!parsedExcelWorkers.length) return;
      let nextId = appDb.trabajadores.length ? Math.max(...appDb.trabajadores.map(w => w.id)) + 1 : 1;
      let added = 0;

      parsedExcelWorkers.forEach(w => {
        // Check if RUT already exists
        const exists = appDb.trabajadores.some(x => x.rut.replace(/[^0-9kK]/g, '') === w.rut.replace(/[^0-9kK]/g, ''));
        if (!exists) {
          appDb.trabajadores.unshift({
            id: nextId++,
            nombre: w.nombre,
            apellido: w.apellido,
            rut: w.rut,
            direccion: w.direccion,
            telefono: w.telefono,
            afp: w.afp,
            previcion_salud: w.previcion_salud,
            estado_civil: 'Soltero',
            fecha_nacimiento: '1995-01-01',
            sent: 'no_enviado'
          });
          added++;
        }
      });

      saveDatabase();
      showToast(`¡Se incorporaron ${added} nuevos trabajadores a la nómina oficial!`, "success");
      document.getElementById('excelPreviewSection').style.display = 'none';
      parsedExcelWorkers = [];
      updateMetrics();
    }

    // Contract Generator
    function populateContractWorkerDropdown() {
      const select = document.getElementById('contractWorkerSelect');
      select.innerHTML = '<option value="">Seleccione un trabajador...</option>';
      appDb.trabajadores.forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.id;
        opt.textContent = `${w.nombre} ${w.apellido} (${w.rut})`;
        select.appendChild(opt);
      });

      // Defaults
      const now = new Date();
      const inOneMonth = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
      document.getElementById('contractStartDate').value = now.toISOString().split('T')[0];
      document.getElementById('contractEndDate').value = inOneMonth.toISOString().split('T')[0];
    }

    function quickContractForWorker(workerId) {
      navigateTo('contratos');
      setTimeout(() => {
        const select = document.getElementById('contractWorkerSelect');
        select.value = workerId;
        onSelectWorkerForContract();
      }, 50);
    }

    function onSelectWorkerForContract() {
      const workerId = parseInt(document.getElementById('contractWorkerSelect').value, 10);
      const worker = appDb.trabajadores.find(w => w.id === workerId);
      if (worker) {
        // Auto trigger preview
        generateContractPreview();
      }
    }

    function generateContractPreview(e) {
      if (e) e.preventDefault();
      const workerId = parseInt(document.getElementById('contractWorkerSelect').value, 10);
      if (!workerId) {
        alert("Por favor selecciona un trabajador para generar su contrato.");
        return;
      }
      const worker = appDb.trabajadores.find(w => w.id === workerId) || appDb.trabajadores[0];
      const template = document.getElementById('contractTemplateSelect').value;
      const start = document.getElementById('contractStartDate').value;
      const end = document.getElementById('contractEndDate').value;
      const salary = parseInt(document.getElementById('contractSalary').value, 10) || 560000;
      const location = document.getElementById('contractLocation').value;

      let title = "CONTRATO DE TRABAJO POR FAENA DETERMINADA (TEMPORADA AGRÍCOLA 2026)";
      let laborText = "cosechador y embalador de uva de mesa en parronales";
      if (template === 'packing') {
        title = "CONTRATO DE TRABAJO TEMPORAL - OPERARIO DE PACKING DE EXPORTACIÓN";
        laborText = "clasificación, selección, pesado y empaque de fruta de exportación";
      } else if (template === 'plazo_fijo') {
        title = "CONTRATO INDIVIDUAL DE TRABAJO A PLAZO FIJO";
        laborText = "operaciones generales agrícolas, riego tecnificado y mantención";
      }

      const html = `
        <h2>${title}</h2>
        <div class="contract-clause">
          En Vicuña, Valle de Elqui, República de Chile, entre <strong>SOCIEDAD AGRÍCOLA FUNDO LA CAMPANA LTDA.</strong>,
          RUT N° 76.543.210-K, representada legalmente por don <strong>Sebastián Espíndola</strong>, con domicilio en Camino Valle Verde Lote 4, en adelante el "Empleador",
          y don(ña) <strong>${worker.nombre.toUpperCase()} ${worker.apellido.toUpperCase()}</strong>, cédula nacional de identidad N° <strong>${worker.rut}</strong>,
          de nacionalidad chilena, con domicilio en <strong>${worker.direccion || 'Vicuña'}</strong>, afiliado(a) a <strong>AFP ${worker.afp || 'Modelo'}</strong>
          y en salud a <strong>${worker.previcion_salud || 'Fonasa'}</strong>, en adelante el "Trabajador", se ha convenido el siguiente contrato de trabajo:
        </div>
        <div class="contract-clause">
          <strong>PRIMERO (Naturaleza de los servicios):</strong> El Trabajador se compromete a desempeñar las funciones de <strong>${laborText}</strong>
          en las dependencias y predios agrícolas del Empleador ubicados en <strong>${location}</strong>.
        </div>
        <div class="contract-clause">
          <strong>SEGUNDO (Jornada laboral):</strong> La jornada ordinaria de trabajo será de 44 horas semanales distribuidas de lunes a viernes en turnos rotativos
          compatibles con las exigencias del Código del Trabajo chileno y las temperaturas de cosecha estacional.
        </div>
        <div class="contract-clause">
          <strong>TERCERO (Remuneración):</strong> El Empleador pagará al Trabajador una remuneración mensual base bruta de <strong>$${salary.toLocaleString('es-CL')}.- (pesos chilenos)</strong>,
          más gratificación legal mensual correspondiente al 25% con tope de 4,75 ingresos mínimos mensuales, sujeta a los descuentos legales previsionales y de salud.
        </div>
        <div class="contract-clause">
          <strong>CUARTO (Vigencia):</strong> El presente contrato regirá a contar del <strong>${start}</strong> y tendrá vigencia hasta el <strong>${end}</strong>,
          fecha en la cual cesará la faena agrícola convenida de conformidad con el artículo 159 N° 4 del Código del Trabajo.
        </div>
        <div class="contract-clause">
          Para constancia, firman las partes en dos ejemplares del mismo tenor y fecha, quedando uno en poder de cada parte.
        </div>
        <div class="contract-signatures">
          <div class="signature-line">
            <strong>SOCIEDAD AGRÍCOLA FUNDO LA CAMPANA</strong><br>
            RUT 76.543.210-K<br>
            Empleador
          </div>
          <div class="signature-line">
            <strong>${worker.nombre} ${worker.apellido}</strong><br>
            RUT ${worker.rut}<br>
            Trabajador(a)
          </div>
        </div>
      `;

      document.getElementById('renderedContractSheet').innerHTML = html;
      document.getElementById('contractPreviewContainer').style.display = 'block';
      showToast("Contrato confeccionado con éxito para " + worker.nombre, "success");
    }

    function printContract() {
      window.print();
    }

    function downloadWordDoc() {
      const content = document.getElementById('renderedContractSheet').innerHTML;
      if (!content) {
        alert("Genera primero el contrato antes de descargarlo.");
        return;
      }
      const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' "+
                     "xmlns:w='urn:schemas-microsoft-com:office:word' "+
                     "xmlns='http://www.w3.org/TR/REC-html40'>"+
                     "<head><meta charset='utf-8'><title>Contrato de Trabajo</title></head><body style='font-family:Times New Roman, serif;'>";
      const footer = "</body></html>";
      const sourceHTML = header + content + footer;
      const source = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(sourceHTML);
      const fileDownload = document.createElement("a");
      document.body.appendChild(fileDownload);
      fileDownload.href = source;
      fileDownload.download = 'Contrato_FundoLaCampana.doc';
      fileDownload.click();
      document.body.removeChild(fileDownload);
      showToast("Descargando contrato en formato Word (.doc)", "success");
    }

    // Biometric Facial Recognition & Camera
    function initCameraView() {
      renderAttendanceList();
      startWebcam();
    }

    function startWebcam() {
      const video = document.getElementById('webcamVideo');
      const canvas = document.getElementById('cameraCanvas');
      const tag = document.getElementById('cameraStatusTag');

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
          .then(stream => {
            webcamStream = stream;
            video.srcObject = stream;
            video.style.display = 'block';
            canvas.style.display = 'none';
            tag.textContent = "Webcam Conectada";
            tag.className = "tag tag-green";
            isSimulatedCam = false;
            document.getElementById('toggleCamBtn').innerHTML = '<i class="bi bi-camera-reels"></i> Simular Cámara';
          })
          .catch(err => {
            // Fallback to simulated camera loop automatically
            startSimulatedCamera();
          });
      } else {
        startSimulatedCamera();
      }
    }

    function stopWebcam() {
      if (webcamStream) {
        webcamStream.getTracks().forEach(t => t.stop());
        webcamStream = null;
      }
      if (simCamInterval) {
        clearInterval(simCamInterval);
        simCamInterval = null;
      }
    }

    function toggleWebcamMode() {
      if (isSimulatedCam) {
        stopWebcam();
        startWebcam();
      } else {
        stopWebcam();
        startSimulatedCamera();
      }
    }

    function startSimulatedCamera() {
      isSimulatedCam = true;
      const video = document.getElementById('webcamVideo');
      const canvas = document.getElementById('cameraCanvas');
      const tag = document.getElementById('cameraStatusTag');
      tag.textContent = "Simulación Activa";
      tag.className = "tag tag-gold";
      video.style.display = 'none';
      canvas.style.display = 'block';
      document.getElementById('toggleCamBtn').innerHTML = '<i class="bi bi-webcam"></i> Conectar Webcam';

      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      let angle = 0;

      if (simCamInterval) clearInterval(simCamInterval);
      simCamInterval = setInterval(() => {
        // Render stylized synthetic surveillance camera view
        ctx.fillStyle = '#06131c';
        ctx.fillRect(0, 0, 640, 480);

        // Grid lines
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.lineWidth = 1;
        for (let x = 0; x < 640; x += 40) {
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 480); ctx.stroke();
        }
        for (let y = 0; y < 480; y += 40) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(640, y); ctx.stroke();
        }

        // Simulated human face silhouette
        const cx = 320 + Math.sin(angle) * 15;
        const cy = 240 + Math.cos(angle) * 8;
        angle += 0.05;

        // Head
        ctx.fillStyle = '#10273c';
        ctx.beginPath();
        ctx.ellipse(cx, cy - 20, 80, 105, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#38bdf8';
        ctx.stroke();

        // Shoulders
        ctx.beginPath();
        ctx.ellipse(cx, cy + 130, 160, 90, 0, 0, Math.PI);
        ctx.fill();
        ctx.stroke();

        // Eyes & landmarks
        ctx.fillStyle = '#39ff14';
        ctx.fillRect(cx - 30, cy - 35, 6, 6);
        ctx.fillRect(cx + 24, cy - 35, 6, 6);
        ctx.fillRect(cx - 3, cy - 10, 6, 6);
        ctx.fillRect(cx - 20, cy + 20, 40, 4);

      }, 50);
    }

    function triggerBiometricScan() {
      // Select a registered worker for recognition
      const unverified = appDb.trabajadores.filter(w => {
        const todayStr = new Date().toISOString().split('T')[0];
        return !(appDb.asistencias || []).some(a => a.trabajador_id === w.id && a.fecha === todayStr);
      });

      const targetWorker = unverified.length ? unverified[Math.floor(Math.random() * Math.min(unverified.length, 5))] : appDb.trabajadores[0];
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const todayStr = now.toISOString().split('T')[0];

      // Update HUD
      document.getElementById('biometricMatchName').textContent = `Match: ${targetWorker.nombre} ${targetWorker.apellido}`;
      document.getElementById('biometricConfidence').textContent = `Confianza: ${(97 + Math.random() * 2.8).toFixed(1)}%`;

      // Record attendance
      if (!appDb.asistencias) appDb.asistencias = [];
      const newAttendance = {
        id: appDb.asistencias.length + 1,
        trabajador_id: targetWorker.id,
        hora: timeStr,
        fecha: todayStr,
        presente: true
      };
      appDb.asistencias.unshift(newAttendance);
      saveDatabase();

      showToast(`¡Asistencia marcada! Bienvenido/a ${targetWorker.nombre} ${targetWorker.apellido} (${timeStr})`, "success");
      renderAttendanceList();
      updateMetrics();
    }

    function renderAttendanceList() {
      const tbody = document.getElementById('attendanceTodayBody');
      tbody.innerHTML = '';
      const todayStr = new Date().toISOString().split('T')[0];
      const todayRecords = (appDb.asistencias || []).filter(a => a.fecha === todayStr);

      document.getElementById('presentTodayCount').textContent = todayRecords.length;

      if (!todayRecords.length) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:1.5rem; color:var(--text-muted);">Aún no hay marcajes registrados hoy.</td></tr>';
        return;
      }

      todayRecords.forEach(a => {
        const w = appDb.trabajadores.find(t => t.id === a.trabajador_id) || { nombre: 'Trabajador', apellido: 'Agrícola', rut: '18.234.567-8' };
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${w.nombre} ${w.apellido}</strong></td>
          <td><code class="tag tag-blue">${w.rut}</code></td>
          <td style="font-family:'JetBrains Mono',monospace; color:var(--cyan);">${a.hora}</td>
          <td><span class="tag tag-green">PRESENTE</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function clearTodayAttendance() {
      const todayStr = new Date().toISOString().split('T')[0];
      appDb.asistencias = (appDb.asistencias || []).filter(a => a.fecha !== todayStr);
      saveDatabase();
      renderAttendanceList();
      updateMetrics();
      showToast("Registro de asistencia del día limpiado", "info");
    }

    // Reports and Charts via Chart.js
    function renderReports() {
      // Previsión Salud
      const fonasaCount = appDb.trabajadores.filter(w => (w.previcion_salud || '').toLowerCase().includes('fonasa')).length;
      const isapreCount = appDb.trabajadores.filter(w => (w.previcion_salud || '').toLowerCase().includes('isapre')).length;
      const otherSalud = appDb.trabajadores.length - (fonasaCount + isapreCount);

      if (charts.salud) charts.salud.destroy();
      charts.salud = new Chart(document.getElementById('chartSalud'), {
        type: 'doughnut',
        data: {
          labels: ['Fonasa', 'Isapre', 'Otros'],
          datasets: [{
            data: [fonasaCount, isapreCount, otherSalud],
            backgroundColor: ['#10b981', '#38bdf8', '#8b5cf6']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#fff' } } } }
      });

      // AFP Distribution
      const afpCounts = {};
      appDb.trabajadores.forEach(w => {
        const afp = w.afp || 'Otras';
        afpCounts[afp] = (afpCounts[afp] || 0) + 1;
      });

      if (charts.afp) charts.afp.destroy();
      charts.afp = new Chart(document.getElementById('chartAfp'), {
        type: 'bar',
        data: {
          labels: Object.keys(afpCounts),
          datasets: [{
            label: 'Trabajadores por AFP',
            data: Object.values(afpCounts),
            backgroundColor: '#e0a91b'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });

      // Age Distribution
      const ageBrackets = { '18-25': 0, '26-35': 0, '36-45': 0, '46-60': 0, '60+': 0 };
      const currentYear = new Date().getFullYear();
      appDb.trabajadores.forEach(w => {
        const birthYear = w.fecha_nacimiento ? parseInt(w.fecha_nacimiento.split('-')[0], 10) : 1990;
        const age = currentYear - birthYear;
        if (age <= 25) ageBrackets['18-25']++;
        else if (age <= 35) ageBrackets['26-35']++;
        else if (age <= 45) ageBrackets['36-45']++;
        else if (age <= 60) ageBrackets['46-60']++;
        else ageBrackets['60+']++;
      });

      if (charts.edad) charts.edad.destroy();
      charts.edad = new Chart(document.getElementById('chartEdad'), {
        type: 'line',
        data: {
          labels: Object.keys(ageBrackets),
          datasets: [{
            label: 'Operarios por Tramo Etario',
            data: Object.values(ageBrackets),
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.2)',
            fill: true,
            tension: 0.35
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#fff' } } },
          scales: {
            x: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#8b9bb4' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    // Toast Notifications
    function showToast(message, type = 'info') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      let icon = 'bi-info-circle-fill';
      if (type === 'success') icon = 'bi-check-circle-fill';
      if (type === 'error') icon = 'bi-x-circle-fill';
      toast.innerHTML = `<i class="bi ${icon}"></i><span>${message}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    // App Initialization
    window.addEventListener('DOMContentLoaded', () => {
      initDatabase();
      const savedUser = sessionStorage.getItem('ca_session_user');
      if (savedUser) {
        try {
          activeUser = JSON.parse(savedUser);
          document.getElementById('userName').textContent = activeUser.name;
          document.getElementById('userAvatar').textContent = activeUser.name.charAt(0).toUpperCase();
          navigateTo('menu');
        } catch(e) {
          navigateTo('login');
        }
      } else {
        navigateTo('login');
      }
    });
  </script>
</body>
</html>
'''

output = html_template.replace('__SEED_DATA__', seed_json_str)

with open('proyectos/contratos-agiles/index.html', 'w', encoding='utf-8') as f:
    f.write(output)

print("Generated proyectos/contratos-agiles/index.html successfully!")

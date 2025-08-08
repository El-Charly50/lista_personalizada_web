let canales = [];
let grupos = [];
let seleccionadosGrupos = new Set();
let seleccionadosCanales = new Set();
let canalesFiltrados = [];
let canalesActivos = [];

function showTab(idx) {
    document.querySelectorAll('.tab').forEach((tab, i) => {
        tab.classList.toggle('active', i === idx);
    });
    document.querySelectorAll('.tab-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === idx);
    });
}

function goToTab(idx) {
    showTab(idx);
}

function cargarM3U() {
    const url = document.getElementById('url').value;
    fetch('/cargar_m3u', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            canales = data.canales;
            grupos = data.grupos;
            seleccionadosGrupos = new Set();
            seleccionadosCanales = new Set();
            mostrarGrupos();
            document.getElementById('btnNext1').disabled = true;
        } else {
            alert(data.error);
        }
    });
}

function mostrarGrupos() {
    let html = '';
    grupos.forEach(g => {
        html += `<label><input type="checkbox" value="${g}" onchange="toggleGrupo('${g}')"> ${g}</label>`;
    });
    document.getElementById('grupos').innerHTML = html;
}

function toggleGrupo(grupo) {
    if (seleccionadosGrupos.has(grupo)) {
        seleccionadosGrupos.delete(grupo);
    } else {
        seleccionadosGrupos.add(grupo);
    }
    document.getElementById('btnNext1').disabled = seleccionadosGrupos.size === 0;
}

function mostrarCanales() {
    let html = '';
    let visibles = 0;
    canales.forEach(c => {
        if (seleccionadosGrupos.has(c.group)) {
            html += `<label><input type="checkbox" value="${c.name}" onchange="toggleCanal('${c.name}')"> ${c.group} - ${c.name}</label>`;
            visibles++;
        }
    });
    document.getElementById('canales').innerHTML = html;
    document.getElementById('btnNext2').disabled = visibles === 0;
}

function toggleCanal(nombre) {
    if (seleccionadosCanales.has(nombre)) {
        seleccionadosCanales.delete(nombre);
    } else {
        seleccionadosCanales.add(nombre);
    }
    document.getElementById('btnNext2').disabled = seleccionadosCanales.size === 0;
}

document.getElementById('btnNext1').onclick = function() {
    mostrarCanales();
    goToTab(1);
};
document.getElementById('btnNext2').onclick = function() {
    canalesFiltrados = canales.filter(c => seleccionadosGrupos.has(c.group) && seleccionadosCanales.has(c.name));
    mostrarVerificacion();
    goToTab(2);
};

function mostrarVerificacion() {
    document.getElementById('verificacion').innerHTML = '';
    document.getElementById('btnNext3').disabled = true;
}

function verificarCanales() {
    document.getElementById('verificacion').innerHTML = 'Verificando...';
    fetch('/verificar_canales', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canales: canalesFiltrados})
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            canalesActivos = data.activos;
            let html = '';
            data.activos.forEach(c => html += `<div>✓ ${c.group} - ${c.name}</div>`);
            data.inactivos.forEach(c => html += `<div style="color:#f55">✗ ${c.group} - ${c.name}</div>`);
            document.getElementById('verificacion').innerHTML = html;
            document.getElementById('btnNext3').disabled = canalesActivos.length === 0;
        } else {
            document.getElementById('verificacion').innerHTML = data.error;
        }
    });
}

document.getElementById('btnNext3').onclick = function() {
    goToTab(3);
};

function descargarM3U() {
    fetch('/descargar_m3u', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canales: canalesActivos})
    })
    .then(resp => resp.blob())
    .then(blob => {
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = "lista_filtrada.m3u";
        a.click();
    });
}

function descargarTXT() {
    fetch('/descargar_txt', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canales: canalesActivos})
    })
    .then(resp => resp.blob())
    .then(blob => {
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = "lista_filtrada.txt";
        a.click();
    });
}
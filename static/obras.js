document.addEventListener('DOMContentLoaded', () => {
  const lista = document.getElementById('lista-obras');
  const qInput = document.getElementById('q');
  const btnSearch = document.getElementById('btn-search');

  function cargar(q='') {
    const url = '/api/obras' + (q ? '?q=' + encodeURIComponent(q) : '');
    fetch(url).then(r=>r.json()).then(data=>{
      lista.innerHTML = '';
      if (!data.length) { lista.innerHTML = '<p>No se encontraron obras.</p>'; return; }
      data.forEach(o=>{
        const div = document.createElement('div');
        div.className = 'card';
        div.innerHTML = `<h3>${o.titulo}</h3><p>Autor: ${o.autor}</p><div class="meta"><span>${o.tipo}</span><span>${o.views} vistas</span></div><div style="margin-top:8px;"><button data-id="${o.id}" class="ver">Ver</button> <button data-id="${o.id}" class="editar">Editar</button></div>`;
        lista.appendChild(div);
      });
    });
  }
  cargar();

  btnSearch.addEventListener('click', ()=> cargar(qInput.value));
  qInput.addEventListener('keyup', (e)=> { if (e.key==='Enter') cargar(qInput.value); });

  lista.addEventListener('click', e=>{
    if (e.target.classList.contains('ver')) {
      const id = e.target.dataset.id;
      window.open('/api/obras/' + id, '_blank');
    } else if (e.target.classList.contains('editar')) {
      const id = e.target.dataset.id;
      window.location.href = '/editar_obra?obra_id=' + id;
    }
  });
});



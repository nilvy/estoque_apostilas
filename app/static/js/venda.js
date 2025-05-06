document.addEventListener("DOMContentLoaded", function () {
  const cursoSelect = document.getElementById("curso_id");
  const matriculaSelect = document.getElementById("matricula_codigo");
  const apostilaSelect = document.getElementById("apostila_id");
  const form = document.getElementById("vendaForm");

  function carregarDependentes() {
    const cursoId = cursoSelect.value;

    if (!cursoId) {
      matriculaSelect.innerHTML =
        '<option value="">Selecione um curso primeiro</option>';
      apostilaSelect.innerHTML =
        '<option value="">Selecione um curso primeiro</option>';
      return;
    }

    // Carrega matrículas
    fetch(`/movimentacoes/api/movimentacoes/matriculas_por_curso/${cursoId}`)
      .then((response) => response.json())
      .then((data) => {
        matriculaSelect.innerHTML =
          '<option value="" selected>Selecione o aluno</option>';
        data.forEach((matricula) => {
          const option = document.createElement("option");
          option.value = matricula.codigo;
          option.textContent = `${matricula.codigo} - ${matricula.nome}`;
          matriculaSelect.appendChild(option);
        });
      });

    // Carrega apostilas
    fetch(`/movimentacoes/api/movimentacoes/apostilas_por_curso/${cursoId}`)
      .then((response) => response.json())
      .then((data) => {
        apostilaSelect.innerHTML =
          '<option value="" selected>Selecione a apostila</option>';
        data.forEach((apostila) => {
          const option = document.createElement("option");
          option.value = apostila.id;
          option.textContent = `${apostila.nome} (${apostila.quantidade} disp.)`;
          if (apostila.quantidade < 1) {
            option.disabled = true;
            option.textContent += " - ESGOTADO";
          }
          apostilaSelect.appendChild(option);
        });
      });
  }

  cursoSelect.addEventListener("change", carregarDependentes);

  // Garante que os selects dinâmicos sejam válidos
  form.addEventListener("submit", function (e) {
    if (!matriculaSelect.value || !apostilaSelect.value) {
      e.preventDefault();
      alert("Selecione um aluno e uma apostila válidos");
    }
  });
});

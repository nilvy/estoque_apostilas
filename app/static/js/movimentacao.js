document.addEventListener("DOMContentLoaded", function () {
  // Confirmação antes de excluir
  document.querySelectorAll(".btn-excluir").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      if (
        !confirm(
          "Tem certeza que deseja excluir esta movimentação?\nEsta ação não pode ser desfeita."
        )
      ) {
        e.preventDefault();
      }
    });
  });
});

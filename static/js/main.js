document.addEventListener("DOMContentLoaded", () => {
  const oldQInput = document.querySelector('input[name="q"]');
  if (oldQInput) {
    const oldForm = oldQInput.closest("form");
    if (oldForm) oldForm.remove();
  }
  // 1) Auto-dismiss flash alerts after 4 seconds
  const alerts = document.querySelectorAll(".alert.auto-dismiss");
  alerts.forEach((a) => {
    setTimeout(() => {
      a.classList.remove("show");
      a.classList.add("hide");
      setTimeout(() => a.remove(), 300);
    }, 4000);
  });

  // 2) Live filter on projects page without reloading
  const liveSearchInput = document.querySelector("#liveProjectSearch");
  const clearBtn = document.querySelector("#clearLiveProjectSearch");

  if (liveSearchInput) {
    function filterCards() {
      const q = liveSearchInput.value.trim().toLowerCase();
      const cards = document.querySelectorAll(".project-card");

      cards.forEach((card) => {
        const text = card.innerText.toLowerCase();
        card.style.display = text.includes(q) ? "" : "none";
      });
    }

    liveSearchInput.addEventListener("input", filterCards);

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        liveSearchInput.value = "";
        filterCards();
        liveSearchInput.focus();
      });
    }
  }

  // 3) Image preview on add/edit project page
  const imageInput = document.querySelector("#projectImageInput");
  const previewImg = document.querySelector("#projectImagePreview");

  if (imageInput && previewImg) {
    imageInput.addEventListener("change", () => {
      const file = imageInput.files && imageInput.files[0];
      if (!file) return;

      const allowed = ["image/png", "image/jpeg", "image/gif", "image/webp"];
      if (!allowed.includes(file.type)) {
        alert("Please select a valid image (png, jpg, jpeg, gif, webp).");
        imageInput.value = "";
        previewImg.classList.add("d-none");
        return;
      }

      const url = URL.createObjectURL(file);
      previewImg.src = url;
      previewImg.classList.remove("d-none");
    });
  }

  // 4) Star rating UI (project detail page)
  const starWrap = document.querySelector("#starRating");
  const ratingInput = document.querySelector("#ratingInput");

  if (starWrap && ratingInput) {
    const stars = starWrap.querySelectorAll("[data-star]");

    function paint(n) {
      stars.forEach((s) => {
        const val = parseInt(s.dataset.star, 10);
        s.classList.toggle("text-warning", val <= n);
        s.classList.toggle("text-muted", val > n);
      });
    }

    stars.forEach((s) => {
      s.style.cursor = "pointer";
      s.addEventListener("click", () => {
        const n = parseInt(s.dataset.star, 10);
        ratingInput.value = String(n);
        paint(n);
      });

      s.addEventListener("mouseenter", () => {
        const n = parseInt(s.dataset.star, 10);
        paint(n);
      });
    });

    starWrap.addEventListener("mouseleave", () => {
      const current = parseInt(ratingInput.value || "0", 10);
      paint(current);
    });

    // paint initial value if already set
    const init = parseInt(ratingInput.value || "0", 10);
    paint(init);
  }
});

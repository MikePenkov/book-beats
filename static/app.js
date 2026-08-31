(() => {
  const key = "book-beats-settings-v1";
  const presets = {
    openai: { model: "gpt-4o-mini", baseUrl: "https://api.openai.com/v1" },
    deepseek: { model: "deepseek-v4-flash", baseUrl: "https://api.deepseek.com" },
  };

  const generating = document.querySelector("[data-generate-url]");
  if (generating) {
    const messages = JSON.parse(generating.dataset.messages);
    const message = generating.querySelector(".generation-message");
    const error = generating.querySelector(".generation-error");
    const retry = generating.querySelector(".retry-generation");
    let index = 0;
    const rotate = setInterval(() => {
      index = (index + 1) % messages.length;
      message.textContent = messages[index];
    }, 2300);
    const runGenerate = () => fetch(generating.dataset.generateUrl, { method: "POST" })
      .then(async (response) => ({ response, body: await response.json() }))
      .then(({ response, body }) => {
        if (!response.ok) throw new Error(body.error || "Request failed");
        clearInterval(rotate);
        window.location.assign(body.next || generating.dataset.previewUrl);
      })
      .catch((failure) => {
        error.hidden = false;
        error.textContent = failure.message;
        retry.hidden = false;
      });
    retry.addEventListener("click", () => {
      retry.hidden = true;
      error.hidden = true;
      message.textContent = messages[0];
      runGenerate();
    });
    runGenerate();
    return;
  }

  const playlistForm = document.querySelector(".playlist-form");
  playlistForm?.addEventListener("submit", () => {
    const button = playlistForm.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = button.dataset.loadingLabel;
  });

  const form = document.querySelector("[data-persist-draft]");
  if (!form) return;
  const save = () => {
    const fields = [...form.elements].filter((field) => field.name && (field.type !== "checkbox" || field.checked));
    localStorage.setItem(key, JSON.stringify(Object.fromEntries(fields.map((field) => [field.name, field.value]))));
  };
  const syncAutoCount = () => {
    const enabled = form.elements.auto_song_count.checked;
    form.elements.song_count.disabled = enabled;
    document.getElementById("count-output").value = enabled ? "AUTO" : form.elements.song_count.value;
  };

  try {
    const draft = JSON.parse(localStorage.getItem(key) || sessionStorage.getItem("book-beats-draft-v1") || "{}");
    Object.entries(draft).forEach(([name, value]) => {
      const field = form.elements.namedItem(name);
      if (field && typeof value === "string") {
        if (field.type === "checkbox") field.checked = value === "1";
        else field.value = value;
      }
    });
    if (sessionStorage.getItem("book-beats-draft-v1")) save();
  } catch (_) {
    localStorage.removeItem(key);
  }

  const provider = form.querySelector("[data-provider]");
  provider?.addEventListener("change", () => {
    const preset = presets[provider.value];
    if (preset) {
      form.elements.model_name.value = preset.model;
      form.elements.base_url.value = preset.baseUrl;
    }
    save();
  });
  form.querySelector("[data-auto-count]").addEventListener("change", () => {
    syncAutoCount();
    save();
  });
  form.querySelector("[data-clear-settings]").addEventListener("click", (event) => {
    event.preventDefault();
    localStorage.removeItem(key);
    sessionStorage.removeItem("book-beats-draft-v1");
    form.reset();
    syncAutoCount();
  });
  syncAutoCount();
  form.addEventListener("input", save);
  form.addEventListener("change", save);
  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = button.dataset.loadingLabel;
  });
})();

document.addEventListener("DOMContentLoaded", () => {
  const datePicker = document.getElementById("datePicker");
  if (datePicker) {
    datePicker.addEventListener("change", () => {
      if (datePicker.value) {
        const nextUrl = new URL(window.location.href);
        nextUrl.searchParams.set("date", datePicker.value);
        window.location.href = nextUrl.toString();
      }
    });
  }

  const modal = document.getElementById("editModal");
  const editForm = document.getElementById("editForm");
  const editTitle = document.getElementById("editTitle");
  const editTime = document.getElementById("editTime");
  const closeModal = document.getElementById("closeModal");

  document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", () => {
      editTitle.value = button.dataset.title || "";
      if (editTime) editTime.value = button.dataset.time || "";
      editForm.action = `/tasks/edit/${button.dataset.id}`;
      modal.classList.add("show");
      editTitle.focus();
    });
  });

  if (closeModal) closeModal.addEventListener("click", () => modal.classList.remove("show"));
  if (modal) {
    modal.addEventListener("click", event => {
      if (event.target === modal) modal.classList.remove("show");
    });
  }

  const drivePhotoInput = document.getElementById("drivePhotoUrl");
  const profileAvatar = document.getElementById("profileAvatar");
  const profileNameInput = document.getElementById("profileName");
  const profilePreviewName = document.getElementById("profilePreviewName");
  const profileAvatarInitial = document.getElementById("profileAvatarInitial");

  if (drivePhotoInput && profileAvatar) {
    const findDriveFileId = value => {
      try {
        const url = new URL(value);
        if (url.hostname !== 'drive.google.com') return null;
        const pathMatch = url.pathname.match(/\/d\/([A-Za-z0-9_-]+)/);
        const id = pathMatch ? pathMatch[1] : url.searchParams.get('id');
        return id && /^[A-Za-z0-9_-]+$/.test(id) ? id : null;
      } catch {
        return null;
      }
    };

    drivePhotoInput.addEventListener("input", () => {
      const fileId = findDriveFileId(drivePhotoInput.value.trim());
      let image = profileAvatar.querySelector("img");
      if (!fileId) {
        if (image) image.remove();
        return;
      }
      if (!image) {
        image = document.createElement("img");
        image.alt = "";
        image.referrerPolicy = "no-referrer";
        image.onerror = () => image.remove();
        profileAvatar.appendChild(image);
      }
      image.src = `https://drive.google.com/thumbnail?id=${encodeURIComponent(fileId)}&sz=w256`;
    });
  }

  if (profileNameInput && profilePreviewName && profileAvatarInitial) {
    profileNameInput.addEventListener("input", () => {
      const name = profileNameInput.value.trim();
      profilePreviewName.textContent = name || "Your name";
      profileAvatarInitial.textContent = name ? name[0].toUpperCase() : "?";
    });
  }
});
  const dhakaClock = document.getElementById("dhakaClock");
  if (dhakaClock) {
    const updateDhakaClock = () => {
      dhakaClock.textContent = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Asia/Dhaka",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      }).format(new Date());
    };
    updateDhakaClock();
    window.setInterval(updateDhakaClock, 1000);
  }


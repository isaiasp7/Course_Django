(function () {
    "use strict";

    const state = {
        agendaId: null,
        selectedSlotId: null,
        slots: []
    };

    const elements = {
        jobList: document.querySelector("[data-js='job-list']"),
        modal: document.querySelector("[data-js='reschedule-modal']"),
        closeButton: document.querySelector("[data-js='close-reschedule']"),
        confirmButton: document.querySelector("[data-js='confirm-reschedule']"),
        slotList: document.querySelector("[data-js='slot-list']"),
        toast: document.querySelector("[data-js='toast']")
    };

    function hasRequiredElements() {
        return Object.values(elements).every(Boolean);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i += 1) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === `${name}=`) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showToast(message) {
        elements.toast.textContent = message;
        elements.toast.hidden = false;
        window.clearTimeout(showToast.timeoutId);
        showToast.timeoutId = window.setTimeout(() => {
            elements.toast.hidden = true;
        }, 2600);
    }

    function renderSlots() {
        elements.confirmButton.disabled = !state.selectedSlotId;

        if (!state.slots.length) {
            elements.slotList.innerHTML = '<p class="slot-empty">Nenhum horario disponivel para este dia.</p>';
            return;
        }

        elements.slotList.innerHTML = state.slots.map((slot) => {
            const selectedClass = slot.id === state.selectedSlotId ? " is-selected" : "";
            return `
                <button class="slot-card${selectedClass}" type="button" data-slot-id="${slot.id}">
                    <span>
                        <strong>${slot.hour}</strong>
                        <span class="slot-card__meta">${slot.date}</span>
                    </span>
                    <span class="slot-card__meta">${slot.label}</span>
                </button>
            `;
        }).join("");
    }

    async function loadSlots(agendaId) {
        state.agendaId = agendaId;
        state.selectedSlotId = null;
        state.slots = [];
        elements.slotList.innerHTML = '<p class="slot-empty">Carregando horarios...</p>';
        elements.confirmButton.disabled = true;
        elements.modal.hidden = false;

        try {
            const response = await fetch(`/dashboard/profissional/remarcar/opcoes/?agenda_id=${encodeURIComponent(agendaId)}`, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            });
            const data = await response.json();

            if (!data.success) {
                elements.slotList.innerHTML = `<p class="slot-empty">${data.error || "Nao foi possivel carregar os horarios."}</p>`;
                return;
            }

            state.slots = data.slots || [];
            renderSlots();
        } catch (error) {
            elements.slotList.innerHTML = '<p class="slot-empty">Erro ao carregar os horarios.</p>';
        }
    }

    async function confirmReschedule() {
        const selectedSlot = state.slots.find((slot) => slot.id === state.selectedSlotId);
        if (!selectedSlot || !state.agendaId) {
            return;
        }

        elements.confirmButton.disabled = true;

        try {
            const response = await fetch("/dashboard/profissional/remarcar/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    agenda_id: state.agendaId,
                    hour: selectedSlot.hour
                })
            });
            const data = await response.json();

            if (!data.success) {
                showToast(data.error || "Nao foi possivel remarcar.");
                elements.confirmButton.disabled = false;
                return;
            }

            const card = document.querySelector(`[data-agenda-id='${state.agendaId}']`);
            if (card) {
                card.querySelector("[data-js='job-hour']").textContent = data.appointment.hora;
            }

            elements.modal.hidden = true;
            showToast(data.message || "Atendimento remarcado com sucesso.");
        } catch (error) {
            showToast("Erro ao remarcar atendimento.");
            elements.confirmButton.disabled = false;
        }
    }

    function bindEvents() {
        elements.jobList.addEventListener("click", (event) => {
            const button = event.target.closest("[data-js='open-reschedule']");
            if (!button) {
                return;
            }

            const card = button.closest("[data-agenda-id]");
            if (card) {
                loadSlots(card.dataset.agendaId);
            }
        });

        elements.slotList.addEventListener("click", (event) => {
            const slotButton = event.target.closest("[data-slot-id]");
            if (!slotButton) {
                return;
            }

            state.selectedSlotId = slotButton.dataset.slotId;
            renderSlots();
        });

        elements.closeButton.addEventListener("click", () => {
            elements.modal.hidden = true;
        });

        elements.modal.addEventListener("click", (event) => {
            if (event.target === elements.modal) {
                elements.modal.hidden = true;
            }
        });

        elements.confirmButton.addEventListener("click", confirmReschedule);
    }

    if (hasRequiredElements()) {
        bindEvents();
    }
})();

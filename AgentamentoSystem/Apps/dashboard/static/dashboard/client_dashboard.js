(function () {
    "use strict";

    const AppState = {
        appointment: {
            professional: "Dr. Joao",
            service: "Corte e finalizacao",
            date: "27/05",
            hour: "14:30",
            duration: "30 minutos",
            location: "Presencial",
            unit: "Studio Centro",
            status: "confirmed"
        },
        selectedSlotId: null,
        slots: [
            { id: "may-28-1030", date: "28/05", label: "Amanha", hour: "10:30", professional: "Dr. Joao" },
            { id: "may-28-1600", date: "28/05", label: "Amanha", hour: "16:00", professional: "Marina" },
            { id: "may-29-0900", date: "29/05", label: "Sexta", hour: "09:00", professional: "Dr. Joao" },
            { id: "may-30-1430", date: "30/05", label: "Sabado", hour: "14:30", professional: "Clara" }
        ],
        notifications: [
            { type: "success", text: "Agendamento confirmado", time: "Hoje, 09:12" },
            { type: "info", text: "Lembrete enviado por WhatsApp", time: "Ontem, 18:40" },
            { type: "warning", text: "Chegue 10 minutos antes", time: "26/05, 08:00" }
        ]
    };

    const StatusMap = {
        confirmed: {
            label: "Confirmado",
            className: "is-confirmed"
        },
        canceled: {
            label: "Cancelado",
            className: "is-canceled"
        }
    };

    const DOM = {
        get(root = document) {
            return {
                status: root.querySelector("[data-js='appointment-status']"),
                professional: root.querySelector("[data-js='professional-name']"),
                service: root.querySelector("[data-js='service-name']"),
                date: root.querySelector("[data-js='appointment-date']"),
                hour: root.querySelector("[data-js='appointment-hour']"),
                duration: root.querySelector("[data-js='appointment-duration']"),
                location: root.querySelector("[data-js='appointment-location']"),
                unit: root.querySelector("[data-js='appointment-unit']"),
                slotList: root.querySelector("[data-js='slot-list']"),
                notificationList: root.querySelector("[data-js='notification-list']"),
                notificationCount: root.querySelector("[data-js='notification-count']"),
                rescheduleButton: root.querySelector("[data-js='reschedule-button']"),
                focusRescheduleButton: root.querySelector("[data-js='focus-reschedule']"),
                openCancelButton: root.querySelector("[data-js='open-cancel']"),
                cancelModal: root.querySelector("[data-js='cancel-modal']"),
                closeCancelButton: root.querySelector("[data-js='close-cancel']"),
                confirmCancelButton: root.querySelector("[data-js='confirm-cancel']"),
                toast: root.querySelector("[data-js='toast']")
            };
        }
    };

    const AppointmentRenderer = {
        render(elements, appointment) {
            elements.professional.textContent = appointment.professional;
            elements.service.textContent = appointment.service;
            elements.date.textContent = appointment.date;
            elements.hour.textContent = appointment.hour;
            elements.duration.textContent = appointment.duration;
            elements.location.textContent = appointment.location;
            elements.unit.textContent = appointment.unit;
            this.renderStatus(elements.status, appointment.status);
        },

        renderStatus(statusElement, status) {
            const statusConfig = StatusMap[status] || StatusMap.confirmed;
            statusElement.textContent = statusConfig.label;
            statusElement.className = `status-pill ${statusConfig.className}`;
        }
    };

    const NotificationRenderer = {
        render(elements, notifications) {
            elements.notificationList.innerHTML = notifications
                .map((notification) => this.createItem(notification))
                .join("");
            elements.notificationCount.textContent = this.getCountLabel(notifications.length);
        },

        createItem(notification) {
            return `
                <article class="notification-item">
                    <span class="notification-icon notification-icon--${notification.type}" aria-hidden="true"></span>
                    <div>
                        <p class="notification-text">${notification.text}</p>
                        <time class="notification-time">${notification.time}</time>
                    </div>
                </article>
            `;
        },

        add(notification) {
            AppState.notifications.unshift(notification);
        },

        getCountLabel(total) {
            return total === 1 ? "1 nova" : `${total} novas`;
        }
    };

    const SlotRenderer = {
        render(elements, slots, selectedSlotId) {
            elements.slotList.innerHTML = slots
                .map((slot) => this.createCard(slot, selectedSlotId))
                .join("");
        },

        createCard(slot, selectedSlotId) {
            const selectedClass = slot.id === selectedSlotId ? " is-selected" : "";

            return `
                <button class="slot-card${selectedClass}" type="button" data-slot-id="${slot.id}">
                    <span class="slot-card__date">${slot.label} - ${slot.date}</span>
                    <span class="slot-card__time">${slot.hour}</span>
                    <span class="slot-card__meta">${slot.professional}</span>
                </button>
            `;
        }
    };

    const Toast = {
        timeoutId: null,

        show(elements, message) {
            window.clearTimeout(this.timeoutId);
            elements.toast.textContent = message;
            elements.toast.hidden = false;

            this.timeoutId = window.setTimeout(() => {
                elements.toast.hidden = true;
            }, 2600);
        }
    };

    const CancelModal = {
        open(elements) {
            elements.cancelModal.hidden = false;
            elements.closeCancelButton.focus();
        },

        close(elements) {
            elements.cancelModal.hidden = true;
        }
    };

    const RescheduleController = {
        bind(elements) {
            elements.slotList.addEventListener("click", (event) => {
                const slotButton = event.target.closest("[data-slot-id]");

                if (!slotButton) {
                    return;
                }

                this.selectSlot(elements, slotButton.dataset.slotId);
            });

            elements.rescheduleButton.addEventListener("click", () => {
                this.confirm(elements);
            });

            elements.focusRescheduleButton.addEventListener("click", () => {
                elements.slotList.scrollIntoView({ behavior: "smooth", block: "center" });
                const firstSlot = elements.slotList.querySelector("[data-slot-id]");

                if (firstSlot) {
                    firstSlot.focus();
                }
            });
        },

        selectSlot(elements, slotId) {
            AppState.selectedSlotId = slotId;
            elements.rescheduleButton.disabled = false;
            SlotRenderer.render(elements, AppState.slots, AppState.selectedSlotId);
        },

        confirm(elements) {
            const selectedSlot = AppState.slots.find((slot) => slot.id === AppState.selectedSlotId);

            if (!selectedSlot) {
                return;
            }

            AppState.appointment.date = selectedSlot.date;
            AppState.appointment.hour = selectedSlot.hour;
            AppState.appointment.professional = selectedSlot.professional;
            AppState.appointment.status = "confirmed";

            NotificationRenderer.add({
                type: "info",
                text: `Horario alterado para ${selectedSlot.date} as ${selectedSlot.hour}`,
                time: "Agora"
            });

            AppState.selectedSlotId = null;
            elements.rescheduleButton.disabled = true;
            App.render();
            Toast.show(elements, "Atendimento reagendado com sucesso.");
        }
    };

    const CancelController = {
        bind(elements) {
            elements.openCancelButton.addEventListener("click", () => CancelModal.open(elements));
            elements.closeCancelButton.addEventListener("click", () => CancelModal.close(elements));

            elements.cancelModal.addEventListener("click", (event) => {
                if (event.target === elements.cancelModal) {
                    CancelModal.close(elements);
                }
            });

            elements.confirmCancelButton.addEventListener("click", () => {
                this.cancelAppointment(elements);
            });
        },

        cancelAppointment(elements) {
            AppState.appointment.status = "canceled";
            NotificationRenderer.add({
                type: "warning",
                text: "Atendimento cancelado pelo cliente",
                time: "Agora"
            });

            CancelModal.close(elements);
            App.render();
            Toast.show(elements, "Atendimento cancelado.");
        }
    };

    const App = {
        elements: null,

        init() {
            this.elements = DOM.get();
            RescheduleController.bind(this.elements);
            CancelController.bind(this.elements);
            this.render();
        },

        render() {
            AppointmentRenderer.render(this.elements, AppState.appointment);
            SlotRenderer.render(this.elements, AppState.slots, AppState.selectedSlotId);
            NotificationRenderer.render(this.elements, AppState.notifications);
        }
    };

    document.addEventListener("DOMContentLoaded", () => App.init());
})();

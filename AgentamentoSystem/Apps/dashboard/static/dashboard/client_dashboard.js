(function () {
    "use strict";

    const emptyAppointment = {
        professional: "Nenhum atendimento",
        service: "Agende um horario para ver os detalhes aqui.",
        date: "--/--",
        hour: "--:--",
        duration: "-",
        location: "-",
        unit: "-",
        status: "empty"
    };

    function getInitialAppointment() {
        const dataElement = document.getElementById("client-dashboard-appointment");
        if (!dataElement) {
            return null;
        }

        try {
            return JSON.parse(dataElement.textContent);
        } catch (error) {
            return null;
        }
    }

    const AppState = {
        appointment: getInitialAppointment() || emptyAppointment,
        selectedSlotId: null,
        slots: [],
        notifications: []
    };

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === `${name}=`) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const StatusMap = {
        confirmed: {
            label: "Confirmado",
            className: "is-confirmed"
        },
        canceled: {
            label: "Cancelado",
            className: "is-canceled"
        },
        empty: {
            label: "Sem agenda",
            className: "is-empty"
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
                rescheduleModal: root.querySelector("[data-js='reschedule-modal']"),
                closeRescheduleButton: root.querySelector("[data-js='close-reschedule']"),
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
            if (!slots.length) {
                elements.slotList.innerHTML = '<p class="slot-empty">Nenhum horario disponivel para este dia.</p>';
                return;
            }

            elements.slotList.innerHTML = slots.map((slot) => this.createCard(slot, selectedSlotId)).join("");
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


    const RescheduleModal = {
        open(elements) {
            elements.rescheduleModal.hidden = false;
            document.body.style.overflow = "hidden";
            const firstSlot = elements.slotList.querySelector("[data-slot-id]");
            if (firstSlot) {
                firstSlot.focus();
            }
        },

        close(elements) {
            elements.rescheduleModal.hidden = true;
            document.body.style.overflow = "";
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

            elements.rescheduleButton.addEventListener("click", async () => {
                await this.confirm(elements);
            });

            elements.focusRescheduleButton.addEventListener("click", async () => {
                RescheduleModal.open(elements);
                await this.loadSlots(elements);
            });

            elements.closeRescheduleButton.addEventListener("click", () => {
                RescheduleModal.close(elements);
            });

            elements.rescheduleModal.addEventListener("click", (event) => {
                if (event.target === elements.rescheduleModal) {
                    RescheduleModal.close(elements);
                }
            });
        },

        async loadSlots(elements) {
            elements.slotList.innerHTML = '<p class="slot-empty">Carregando horarios...</p>';
            elements.rescheduleButton.disabled = true;
            AppState.selectedSlotId = null;

            try {
                const response = await fetch("/dashboard/remarcar/opcoes/", {
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

                AppState.slots = data.slots || [];
                SlotRenderer.render(elements, AppState.slots, AppState.selectedSlotId);
            } catch (error) {
                elements.slotList.innerHTML = '<p class="slot-empty">Erro ao carregar os horarios.</p>';
            }
        },

        selectSlot(elements, slotId) {
            AppState.selectedSlotId = slotId;
            elements.rescheduleButton.disabled = false;
            SlotRenderer.render(elements, AppState.slots, AppState.selectedSlotId);
        },

        async confirm(elements) {
            const selectedSlot = AppState.slots.find((slot) => slot.id === AppState.selectedSlotId);

            if (!selectedSlot) {
                return;
            }

            elements.rescheduleButton.disabled = true;

            try {
                const response = await fetch("/dashboard/remarcar/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({
                        hour: selectedSlot.hour
                    })
                });
                const data = await response.json();

                if (!data.success) {
                    elements.rescheduleButton.disabled = false;
                    Toast.show(elements, data.error || "Nao foi possivel remarcar.");
                    return;
                }

                AppState.appointment = data.appointment;
                NotificationRenderer.add({
                    type: "info",
                    text: `Horario alterado para ${data.appointment.date} as ${data.appointment.hour}`,
                    time: "Agora"
                });

                AppState.selectedSlotId = null;
                AppState.slots = [];
                RescheduleModal.close(elements);
                App.render();
                Toast.show(elements, data.message || "Atendimento remarcado com sucesso.");
            } catch (error) {
                elements.rescheduleButton.disabled = false;
                Toast.show(elements, "Erro ao remarcar atendimento.");
            }
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

            elements.confirmCancelButton.addEventListener("click", async () => {
                await this.cancelAppointment(elements);
            });
        },

        async cancelAppointment(elements) {
            elements.confirmCancelButton.disabled = true;

            try {
                const response = await fetch("/dashboard/cancelar/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    }
                });
                const data = await response.json();

                if (!data.success) {
                    elements.confirmCancelButton.disabled = false;
                    Toast.show(elements, data.error || "Nao foi possivel cancelar.");
                    return;
                }

                AppState.appointment = data.appointment;
                NotificationRenderer.add({
                    type: "warning",
                    text: "Atendimento cancelado pelo cliente",
                    time: "Agora"
                });

                CancelModal.close(elements);
                App.render();
                Toast.show(elements, data.message || "Atendimento cancelado.");
            } catch (error) {
                Toast.show(elements, "Erro ao cancelar atendimento.");
            } finally {
                elements.confirmCancelButton.disabled = false;
            }
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

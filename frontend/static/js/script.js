document.addEventListener('DOMContentLoaded', function() {
    // Обработка кликов на сердечко
    document.addEventListener('click', async function(e) {
         if (e.target.closest('.navbar') || e.target.closest('.menu-items')) {
            return; // Не обрабатываем клики в хедере
        }
        if (e.target.closest('.favourite-btn') || e.target.classList.contains('fa-heart')) {
            e.preventDefault();
            const heart = e.target.classList.contains('fa-heart') ? e.target : e.target.querySelector('.fa-heart');
            const eventId = e.target.closest('[data-event-id]').getAttribute('data-event-id');

            try {
                const response = await fetch(`/events/event/${eventId}/favourite`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include'
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'added') {
                        heart.classList.replace('far', 'fas');
                        heart.style.color = 'red';
                    } else {
                        heart.classList.replace('fas', 'far');
                        heart.style.color = '#757575';
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });
});
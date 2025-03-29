const kabir = document.querySelector('.kabir');
const saniya = document.querySelector('.sania');

kabir.addEventListener('mouseover', () => {
    kabir.style.transform = 'scale(1.1)';
});

kabir.addEventListener('mouseout', () => {
    kabir.style.transform = 'scale(1)';
});

saniya.addEventListener('mouseover', () => {
    saniya.style.transform = 'scale(1.1)';
});

saniya.addEventListener('mouseout', () => {
    saniya.style.transform = 'scale(1)';
});

// Hotel tips array
const hotelTips = [
    "Book your hotel room during off-peak seasons for better rates",
    "Always check online reviews before making a reservation",
    "Consider location - being close to attractions can save on transportation",
    "Look for hotels with complimentary breakfast to save on meals",
    "Check if the hotel has a pool or gym if those amenities are important to you",
    "Read the cancellation policy carefully before booking",
    "Consider booking directly with the hotel for potential perks",
    "Check if the hotel offers airport shuttle service",
    "Look for hotels with 24-hour front desk service",
    "Consider the view from your room - it might be worth the upgrade"
];

// Function to update hotel tips
function updateHotelTip() {
    const tipElement = document.getElementById('tip-text');
    if (!tipElement) return;

    let currentIndex = 0;
    
    function showNextTip() {
        // Fade out
        tipElement.style.opacity = '0';
        
        setTimeout(() => {
            // Update text
            tipElement.textContent = hotelTips[currentIndex];
            
            // Fade in
            tipElement.style.opacity = '1';
            
            // Move to next tip
            currentIndex = (currentIndex + 1) % hotelTips.length;
        }, 500);
    }

    // Initial tip
    showNextTip();
    
    // Update every 3 seconds
    setInterval(showNextTip, 3000);
}

// Scroll Animation
function handleScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.fade-in').forEach((element) => {
        observer.observe(element);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    updateHotelTip();
    handleScrollAnimations();
});
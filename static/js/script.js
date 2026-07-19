// ===========================================
// Bundle E-Commerce JavaScript
// ===========================================

// Loading Animation

window.addEventListener("load", function () {

    document.body.classList.add("loaded");

});

// ===========================================
// Navbar Shadow
// ===========================================

window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 20) {

        navbar.classList.add("shadow-lg");

    } else {

        navbar.classList.remove("shadow-lg");

    }

});

// ===========================================
// Back To Top Button
// ===========================================

const topButton = document.createElement("button");

topButton.innerHTML = "↑";

topButton.id = "topButton";

document.body.appendChild(topButton);

topButton.style.position = "fixed";
topButton.style.bottom = "20px";
topButton.style.right = "20px";
topButton.style.width = "50px";
topButton.style.height = "50px";
topButton.style.border = "none";
topButton.style.borderRadius = "50%";
topButton.style.background = "#ffc107";
topButton.style.color = "#000";
topButton.style.fontSize = "22px";
topButton.style.cursor = "pointer";
topButton.style.display = "none";
topButton.style.zIndex = "999";

window.addEventListener("scroll", function () {

    if (window.scrollY > 300) {

        topButton.style.display = "block";

    } else {

        topButton.style.display = "none";

    }

});

topButton.onclick = function () {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

};

// ===========================================
// Product Hover Animation
// ===========================================

document.querySelectorAll(".card").forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-10px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});

// ===========================================
// Search Validation
// ===========================================

const searchForm = document.querySelector("form");

if (searchForm) {

    searchForm.addEventListener("submit", function (e) {

        const input = searchForm.querySelector("input");

        if (input.value.trim() === "") {

            e.preventDefault();

            alert("Please enter a product name.");

        }

    });

}

// ===========================================
// Add To Cart Animation
// ===========================================

document.querySelectorAll(".btn-warning").forEach(button => {

    if (button.innerText.includes("Cart")) {

        button.addEventListener("click", function () {

            button.innerHTML = "✔ Added";

            setTimeout(() => {

                button.innerHTML = "Add To Cart";

            }, 1500);

        });

    }

});

// ===========================================
// Newsletter Validation
// ===========================================

const emailInput = document.querySelector("input[type='email']");

if (emailInput) {

    emailInput.addEventListener("change", function () {

        if (!emailInput.value.includes("@")) {

            alert("Please enter a valid email.");

        }

    });

}

// ===========================================
// Image Zoom Effect
// ===========================================

document.querySelectorAll(".card img").forEach(img => {

    img.addEventListener("mouseover", function () {

        img.style.transform = "scale(1.08)";

        img.style.transition = ".4s";

    });

    img.addEventListener("mouseout", function () {

        img.style.transform = "scale(1)";

    });

});

// ===========================================
// Countdown Timer
// ===========================================

let countdown = 86400;

const timer = document.getElementById("dealTimer");

if (timer) {

    setInterval(function () {

        let h = Math.floor(countdown / 3600);

        let m = Math.floor((countdown % 3600) / 60);

        let s = countdown % 60;

        timer.innerHTML =

            h + "h " +

            m + "m " +

            s + "s";

        countdown--;

        if (countdown < 0) {

            countdown = 86400;

        }

    }, 1000);

}

// ===========================================
// Smooth Scroll
// ===========================================

document.querySelectorAll("a[href^='#']").forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(this.getAttribute("href"))

            .scrollIntoView({

                behavior: "smooth"

            });

    });

});

// ===========================================
// Welcome Message
// ===========================================

console.log("Welcome to Bundle Fashion Store");

// ===========================================
// End
// ===========================================
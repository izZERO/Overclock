const baseHtmlEL = document.documentElement
const darkmodeSwitch = document.getElementById("darkmode-switch")
const logoEl = document.querySelector(".image-header")

if (!localStorage.getItem("isDarkmode")) {
  localStorage.setItem("isDarkmode", "false")
}

if (localStorage.getItem("isDarkmode") === "true") {
  baseHtmlEL.setAttribute("data-bs-theme", "dark")
  logoEl.setAttribute("style", "filter: brightness(0) invert(1);")
  darkmodeSwitch.checked = true
} else {
  baseHtmlEL.setAttribute("data-bs-theme", "light")

  logoEl.setAttribute("style", "filter: brightness(0);")
  darkmodeSwitch.checked = false
}

darkmodeSwitch.addEventListener("click", () => {
  const isDarkmode = localStorage.getItem("isDarkmode")

  if (isDarkmode === "true") {
    baseHtmlEL.setAttribute("data-bs-theme", "light")
    localStorage.setItem("isDarkmode", "false")
    logoEl.setAttribute("style", "filter: brightness(0);")

    darkmodeSwitch.checked = false
  } else {
    baseHtmlEL.setAttribute("data-bs-theme", "dark")
    localStorage.setItem("isDarkmode", "true")
    logoEl.setAttribute("style", "filter: brightness(0) invert(1);")
    darkmodeSwitch.checked = true
  }
})

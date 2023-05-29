window.addEventListener('load', e => {
    submitSearch()

    fileInputUpdatePath()

    dateTimeShortcutsOverlay()
})

/*************************************************************
 * Calendar & clock
 *************************************************************/
const dateTimeShortcutsOverlay = () => {
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutationRecord => {
            const display = mutationRecord.target.style.display
            const overlay = document.getElementById('modal-overlay')

            if (display === 'block') {
                overlay.style.display = 'block'
            } else {
                overlay.style.display = 'none'
            }
        });
    });

    const targets = document.querySelectorAll('.calendarbox, .clockbox')

    Array.from(targets).forEach(target => {
        observer.observe(target, {
            attributes: true,
            attributeFilter: ['style']
        });
    })
}

/*************************************************************
 * File upload path
 *************************************************************/
const fileInputUpdatePath = () => {
    const updateFilePath = () => {
        Array.from(document.querySelectorAll('input[type=file]')).forEach(input => {
            input.addEventListener('change', e => {
                const parts = e.target.value.split('\\')
                const placeholder = input.parentNode.parentNode.querySelector('input[type=text]')
                placeholder.setAttribute('value', parts[parts.length - 1])
            })
        })
    }

    updateFilePath()

    document.addEventListener('DOMNodeInserted', e => {
        updateFilePath()
    })
}

/*************************************************************
 * Search form on changelist view
 *************************************************************/
const submitSearch = () => {
    const searchbar = document.getElementById('searchbar')
    const searchbarSubmit = document.getElementById('searchbar-submit')

    if (searchbar !== null) {
        searchbar.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                window.location = `?q=${e.target.value}`
                e.preventDefault()
            } else {

            }
        })
    }

    if (searchbarSubmit !== null && searchbar !== null) {
        searchbarSubmit.addEventListener('click', e => {
            e.preventDefault()
            window.location = `?q=${searchbar.value}`
        })
    }
}

// Markdown Editor Configuration for Django Unfold
// Uses EasyMDE with custom styling

document.addEventListener('DOMContentLoaded', function() {
    const markdownTextareas = document.querySelectorAll('textarea[id^="markdown-"]');
    
    markdownTextareas.forEach(function(textarea) {
        if (textarea.easymde) {
            return;
        }

        const easymde = new EasyMDE({
            element: textarea,
            spellChecker: false,
            autosave: {
                enabled: false,
            },
            status: ['lines', 'words', 'cursor'],
            toolbar: [
                "bold",
                "italic", 
                "strikethrough",
                "|",
                "heading-1",
                "heading-2",
                "heading-3",
                "|",
                "quote",
                "code",
                "unordered-list",
                "ordered-list",
                "|",
                "link",
                "image",
                "table",
                "horizontal-rule",
                "|",
                "preview",
                "side-by-side",
                "fullscreen",
                "|",
                "guide"
            ],
            renderingConfig: {
                codeSyntaxHighlighting: false,
            },
            sideBySideFullscreen: true,
            initialValue: textarea.value,
        });

        textarea.easymde = easymde;

        // Watch for theme changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'class') {
                    const isDark = document.documentElement.classList.contains('dark');
                    const wrapper = textarea.closest('.markdown-widget-wrapper');
                    if (wrapper) {
                        if (isDark) {
                            wrapper.classList.add('dark');
                        } else {
                            wrapper.classList.remove('dark');
                        }
                    }
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        });
    });
});


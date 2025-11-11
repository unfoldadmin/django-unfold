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
                {
                    name: "bold",
                    action: EasyMDE.toggleBold,
                    className: "unfold-markdown-button",
                    title: "Bold",
                },
                {
                    name: "italic",
                    action: EasyMDE.toggleItalic,
                    className: "unfold-markdown-button",
                    title: "Italic",
                },
                {
                    name: "strikethrough",
                    action: EasyMDE.toggleStrikethrough,
                    className: "unfold-markdown-button",
                    title: "Strikethrough",
                },
                "|",
                {
                    name: "heading-1",
                    action: EasyMDE.toggleHeading1,
                    className: "unfold-markdown-button",
                    title: "Heading 1",
                },
                {
                    name: "heading-2",
                    action: EasyMDE.toggleHeading2,
                    className: "unfold-markdown-button",
                    title: "Heading 2",
                },
                {
                    name: "heading-3",
                    action: EasyMDE.toggleHeading3,
                    className: "unfold-markdown-button",
                    title: "Heading 3",
                },
                "|",
                {
                    name: "quote",
                    action: EasyMDE.toggleBlockquote,
                    className: "unfold-markdown-button",
                    title: "Quote",
                },
                {
                    name: "code",
                    action: EasyMDE.toggleCodeBlock,
                    className: "unfold-markdown-button",
                    title: "Code",
                },
                {
                    name: "unordered-list",
                    action: EasyMDE.toggleUnorderedList,
                    className: "unfold-markdown-button",
                    title: "Unordered List",
                },
                {
                    name: "ordered-list",
                    action: EasyMDE.toggleOrderedList,
                    className: "unfold-markdown-button",
                    title: "Ordered List",
                },
                "|",
                {
                    name: "link",
                    action: EasyMDE.drawLink,
                    className: "unfold-markdown-button",
                    title: "Link",
                },
                {
                    name: "image",
                    action: EasyMDE.drawImage,
                    className: "unfold-markdown-button",
                    title: "Image",
                },
                {
                    name: "table",
                    action: EasyMDE.drawTable,
                    className: "unfold-markdown-button",
                    title: "Table",
                },
                {
                    name: "horizontal-rule",
                    action: EasyMDE.drawHorizontalRule,
                    className: "unfold-markdown-button",
                    title: "Horizontal Rule",
                },
                "|",
                {
                    name: "preview",
                    action: EasyMDE.togglePreview,
                    className: "unfold-markdown-button no-disable",
                    title: "Preview",
                },
                {
                    name: "side-by-side",
                    action: EasyMDE.toggleSideBySide,
                    className: "unfold-markdown-button no-disable no-mobile",
                    title: "Side by Side",
                },
                {
                    name: "fullscreen",
                    action: EasyMDE.toggleFullScreen,
                    className: "unfold-markdown-button no-disable no-mobile",
                    title: "Fullscreen",
                },
                "|",
                {
                    name: "guide",
                    action: "https://www.markdownguide.org/basic-syntax/",
                    className: "unfold-markdown-button",
                    title: "Markdown Guide",
                }
            ],
            renderingConfig: {
                codeSyntaxHighlighting: false,
            },
            initialValue: textarea.value,
        });

        // Replace FA icons with Material Symbols
        setTimeout(() => {
            const iconMap = {
                'bold': 'format_bold',
                'italic': 'format_italic',
                'strikethrough': 'format_strikethrough',
                'heading-1': 'format_h1',
                'heading-2': 'format_h2',
                'heading-3': 'format_h3',
                'quote': 'format_quote',
                'code': 'code',
                'unordered-list': 'format_list_bulleted',
                'ordered-list': 'format_list_numbered',
                'link': 'link',
                'image': 'image',
                'table': 'table',
                'horizontal-rule': 'horizontal_rule',
                'preview': 'visibility',
                'side-by-side': 'view_sidebar',
                'fullscreen': 'fullscreen',
                'guide': 'help'
            };

            const toolbar = textarea.parentElement.querySelector('.editor-toolbar');
            if (toolbar) {
                Object.keys(iconMap).forEach(name => {
                    const button = toolbar.querySelector(`button.${name}`);
                    if (button) {
                        button.innerHTML = '';
                        const span = document.createElement('span');
                        span.className = 'material-symbols-outlined';
                        span.textContent = iconMap[name];
                        button.appendChild(span);
                    }
                });
            }
        }, 50);

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


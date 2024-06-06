function deleteUserInput(){
    var result = confirm("Want to delete?");
    if (result) {
        document.getElementById("input_text").value = "";
        document.getElementById("input_form").submit();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const pasteButton = document.getElementById('paste_btn');
    const textArea = document.getElementById('input_text');
    const textForm = document.getElementById('input_form');

    textForm.addEventListener('submit', (event) => {
        event.preventDefault();
    });

    pasteButton.addEventListener('click', async () => {
        try {

            if (navigator.clipboard) {

                const text = await navigator.clipboard.readText();

                textArea.value = text;

                textForm.submit();
            } else {
                alert('Clipboard API not supported in this browser');
            }
        } catch (err) {
            console.error('Failed to read clipboard contents: ', err);
        }
    });
});
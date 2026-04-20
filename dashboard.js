document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('authToken');
    let currentEditId = null;

    if (!token) {
        window.location.href = 'index.html';
        return;
    }
        
    // Fetch user data
    try {
        const response = await fetch('http://127.0.0.1:5000/api/protected-data', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('welcomeMessage').innerText = data.message;
        } else {
            throw new Error('Invalid token');
        }
    } catch (error) {
        console.error('Auth error:', error);
        localStorage.removeItem('authToken');
        window.location.href = 'index.html'
        return;
    }

    // Function to delete notes
    const deleteNote = async (noteId) => {
        try{
            const response = await fetch(`http://127.0.0.1:5000/api/notes/${noteId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok){
                if (currentEditId === noteId){
                    document.getElementById('noteInput').value = '';
                    currentEditId = null;
                    document.getElementById('saveNoteBtn').innerText = 'Salvar nota';
                }
                loadNotes();
            } else{
                console.error("Não conseguimos apagar a nota");
            }
        } catch (error){
            console.error('Erro ao deletar a nota:', error);
        }
    };

    // Function to load notes
    const loadNotes = async () => {
        try{
            const response = await fetch('http://127.0.0.1:5000/api/notes', {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}`}
            });
            const notes = await response.json();

            const container = document.getElementById('notesContainer');
            container.innerHTML = '';

            if (notes.length == 0){
                container.innerHTML = '<p style="text-align: center; color #999;">Sem anotações.</p>';
                return;
            }

            notes.forEach(note => {
                const date = new Date(note.created_at).toLocaleString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                const noteHTML = `
                    <div class="note-card">
                        <div class="note-header">
                            <div class="note-date">${date}</div>
                            <div class="btn-group">
                                <button class="edit-btn" data-id="${note.id}">Edit</button>
                                <button class="delete-btn" data-id="${note.id}">Deletar</button>
                            </div>        
                        </div>
                        <p class="note-content" id="content-${note.id}">${note.content}</p>
                    </div>
                `;
                container.innerHTML += noteHTML;
            });
            
            const deleteButtons = document.querySelectorAll('.delete-btn');
            deleteButtons.forEach(button => {
                button.addEventListener('click', async (event) => {
                    const noteId = event.target.getAttribute('data-id');
                    if (confirm('Tem certeza que deseja apagar essa nota?')) {
                        await deleteNote(noteId);
                    }
                });
            });

            const editButtons = document.querySelectorAll('.edit-btn');
            editButtons.forEach(button => {
                button.addEventListener('click', (event) => {
                    const noteId = event.target.getAttribute('data-id');
                    const contentElement = document.getElementById(`content-${noteId}`);
                    const noteInput = document.getElementById('noteInput');
                    const saveBtn = document.getElementById('saveNoteBtn');

                    noteInput.value = contentElement.innerText;
                    currentEditId = noteId;
                    saveBtn.innerText = 'Atualizar nota';
                });
            });

        } catch (error) {
            console.error('Error loading notes:', error);
        }
    };

    // Initial load
    loadNotes();

    // Save new note
    document.getElementById('saveNoteBtn').addEventListener('click', async () => {
        const noteInput = document.getElementById('noteInput');
        const content = noteInput.value.trim();

        if (!content) return;

        try {
            let url = 'http://127.0.0.1:5000/api/notes';
            let method = 'POST';

            if (currentEditId) {
                url = `http://127.0.0.1:5000/api/notes/${currentEditId}`;
                method = 'PUT';
            }
                
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({content: content})
            });

            if (response.ok) {
                noteInput.value = '';
                currentEditId = null;
                document.getElementById('saveNoteBtn').innerText = 'Salvar nota';
                loadNotes();
            }
        } catch (error){
            console.error('Error saving notes:', error);
        }
    });

    // Search filter
    document.getElementById('searchInput').addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();
        const noteCards = document.querySelectorAll('.note-card');

        noteCards.forEach(card => {
            const noteText = card.querySelector('.note-content').innerText.toLowerCase();

            if (noteText.includes(searchTerm)) {
                card.style.display = 'flex'; // Shows the matching texting in note
            }
            else{
                card.style.display = 'none'; // Hide note without the characters
            }
        })
    })

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('authToken');
        window.location.href = 'index.html';
    });
});
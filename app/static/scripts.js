// Gestione chiamate asincrone
async function fetchWitnesses() {
    const response = await fetch('/get_witnesses/');
    const witnesses = await response.json();
    updateWitnessesList(witnesses);
};

function updateWitnessesList(witnesses) {
    const tableBody = document.querySelector('#witnesses-table tbody');
    tableBody.innerHTML = ''; // Pulisci il contenuto della tabella

    witnesses.forEach(witness => {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = witness.name;
        row.appendChild(nameCell);

        const actionCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Rimuovi';
        deleteButton.onclick = () => deleteWitness(witness.id);
        actionCell.appendChild(deleteButton);
        row.appendChild(actionCell);

        tableBody.appendChild(row);
    });

    updateWitnessesTitle(); // Aggiorna il titolo dopo aver aggiornato la lista
};

async function deleteWitness(id) {
    const witObj = { witness_id: id };

    const response = await fetch('/delete_witness/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(witObj)
    });
    if (response.ok) {
        alert('Testimone rimosso con successo!');
        fetchWitnesses();  // Ricarica la lista dei testimoni
        updateWitnessesTitle(); // Aggiorna il titolo
    } else {
        alert('Errore nella rimozione del testimone');
    };
};

window.onload = function() {
    fetchWitnesses();
    updateWitnessesTitle(); // Aggiorna il titolo quando la pagina viene caricata
};
// Funzione per caricare i lemmatizzatori dal backend
async function loadLemmatizers() {
    const response = await fetch('/lemmatizers/');
    const lemmatizers = await response.json();
    const lemmatizerSelect = document.getElementById('lemmatizer');
    lemmatizers.forEach(lemmatizer => {
        const option = document.createElement('option');
        option.value = lemmatizer;
        option.textContent = lemmatizer;
        lemmatizerSelect.appendChild(option);
    });
}

// Chiamare la funzione per caricare i lemmatizzatori quando la pagina viene caricata
document.addEventListener('DOMContentLoaded', loadLemmatizers);

// Disabilita il caricamento dei testimoni se l'area è vuota
document.getElementById('witness-text-area').addEventListener('input', function() {
    const text = document.getElementById('witness-text-area').value;
    const addButton = document.getElementById('addWitnessButton');

    if (text.trim().length > 0) {
        addButton.disabled = false; // Abilita il bottone se c'è testo
    } else {
        addButton.disabled = true; // Disabilita il bottone se non c'è testo
    }
});

// Form per l'aggiunta del testimone
document.getElementById('addWitnessForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const text = document.getElementById('witness-text-area').value;

    // Controlla se il nome è vuoto
    if (name === '') {
        alert('Errore: il nome del testimone non può essere vuoto.');

        return;
    };

    // Controlla se il nome esiste già nella tabella dei testimoni
    const witnessNames = Array.from(
        document.querySelectorAll('#witnesses-table tbody tr td:first-child')
    ).map(td => td.textContent.trim().toLowerCase());

    if (witnessNames.includes(name.toLowerCase())) {
        alert('Errore: esiste già un testimone con questo nome.');

        return;
    };

    // Invia la richiesta per aggiungere il testimone
    const witToAdd = {
            witness_name: name,
            witness_text: text,
        };

    const response = await fetch('/add_witness/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(witToAdd),
    });

    const result = await response.json();

    if (response.ok) {
        alert('Testimone aggiunto con successo!');
        document.getElementById('name').value = '';
        document.getElementById('witness-text-area').value = '';
        document.getElementById('addWitnessButton').disabled = true; // Disabilita il bottone dopo l'aggiunta
        // Se necessario, aggiorna la lista dei testimoni senza ricaricare la pagina
        updateWitnessesList(result.witnesses);
        updateWitnessesTitle(); // Aggiorna il titolo
    } else {
        alert(`Errore: ${result.detail || 'Impossibile aggiungere il testimone'}`);
    }
});

// Gestione del form di collazione
document.getElementById('collationForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const selectedLemmatizer = document.getElementById('lemmatizer').value;

    if (!selectedLemmatizer) {
        alert('Seleziona un lemmatizzatore prima di avviare la collazione.');
        return;
    };

    // Conta il numero di testimoni nella tabella
    const witnessTable = document.getElementById('witnesses-table');
    const witnessCount = witnessTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;

    if (witnessCount < 2) {
        alert('Servono almeno due testimoni per avviare la collazione.');
        return;
    };

    // Usa fetchWithLoading per avviare la collazione senza cambiare pagina
    const url = `/collation/?lemmatizer=${encodeURIComponent(selectedLemmatizer)}`;

    try {
        const response = await fetchWithLoading(url, { method: 'GET' });

        if (response.ok) {
            // Qui puoi gestire la risposta, ad esempio:
            const result = await response.json();
            // Mostra il risultato nella pagina corrente, oppure...
            let collationDiv = document.getElementById("collationHTMLtable");

            // Se l'elemento non esiste, crealo
            if (!collationDiv) {
                collationDiv = document.createElement('div');
                collationDiv.id = "collationHTMLtable";
                collationDiv.style.textAlign = "center"; // Stile opzionale, come prima
                document.body.appendChild(collationDiv);
            };
            collationDiv.innerHTML = `        <h2>Risultato della Collazione</h2>${result.collation_html}`;
            // ... o naviga a una nuova pagina:
            // window.location.href = url; (se proprio vuoi navigare dopo aver ricevuto una risposta positiva)

            // Aggiorna il bottone "Save Collection"
            updateSaveCollationButton();

            // Abilita la selezione delle celle dopo aver caricato la collazione
            enableCellSelection();
        } else {
            alert('Errore durante la collazione.');
        }
    } catch (error) {
        console.error('Errore nella richiesta:', error);
        alert('Errore nella connessione al server.');
    };
});

document.getElementById('saveCollationButton').addEventListener('click', async function() {
    const collationName = prompt("Inserisci il nome per la collazione:");
    if (!collationName) return;

    const collationHtml = document.querySelector("#collationHTMLtable").innerHTML;
    const response = await fetch('/save_collation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: collationName, html_table: collationHtml }),
    });

    const result = await response.json();
    if (response.ok) {
        alert('Collazione salvata con successo!');
        if (document.getElementById('collations-table')) {
            const savedColsBtn = document.getElementById('savedCollationsButton');
            savedColsBtn.click();
        };
    } else {
        alert(`Errore: ${result.detail}`);
    }
});

document.getElementById('savedCollationsButton').addEventListener('click', async function() {
    const savedCollationsList = document.getElementById('savedCollationsList');
    savedCollationsList.style.display = 'block'; // Mostra la lista delle collazioni salvate

    const response = await fetch('/get_collations/');
    const collations = await response.json();

    // Controllo se la lista delle collazioni è vuota
    if (collations.length === 0) {
        alert('Nessuna Collazione presente nel Database.');

        return; // Esce dalla funzione se non ci sono collazioni
    };

    const tableBody = document.querySelector('#collations-table tbody');
    tableBody.innerHTML = ''; // Pulisci il contenuto della tabella

    collations.forEach(collation => {
        const row = document.createElement('tr');
        const nameCell = document.createElement('td');
        nameCell.textContent = collation.name;
        row.appendChild(nameCell);

        const actionCell = document.createElement('td');

        const loadButton = document.createElement('button');
        loadButton.textContent = 'Carica';
        loadButton.onclick = async () => {
            const response = await fetch('/load_collation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: collation.name }),
            });
            const result = await response.json();
            if (response.ok) {
                let collationDiv = document.getElementById("collationHTMLtable");

                // Se l'elemento non esiste, crealo
                if (!collationDiv) {
                    collationDiv = document.createElement('div');
                    collationDiv.id = "collationHTMLtable";
                    collationDiv.style.textAlign = "center"; // Stile opzionale, come prima
                    document.body.appendChild(collationDiv);
                }

                if (document.getElementById("collationTitle")) {
                    document.getElementById("collationTitle").innerHTML = "";
                };
                collationDiv.innerHTML = `        <h2>${collation.name}</h2>${result.html_table}`;
                updateSaveCollationButton();  // Aggiorna lo stato del bottone
                enableCellSelection();  // Abilitare la selezione delle celle
            } else {
                alert(`Errore: ${result.detail}`);
            };
        };
        actionCell.appendChild(loadButton);

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Rimuovi';
        deleteButton.onclick = async () => {
            const response = await fetch('/delete_collation/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: collation.name }),
            });
            const result = await response.json();
            if (response.ok) {
                alert('Collazione rimossa con successo!');
                row.remove();
                updateSaveCollationButton();  // Aggiorna lo stato del bottone
            } else {
                alert(`Errore: ${result.detail}`);
            }
        };
        actionCell.appendChild(deleteButton);

        row.appendChild(actionCell);
        tableBody.appendChild(row);
    });
});

// Funzione per aggiornare lo stato del bottone "Salva Collazione"
function updateSaveCollationButton() {
    const collationDiv = document.getElementById("collationHTMLtable");
    const saveButton = document.getElementById('saveCollationButton');

    if (collationDiv && collationDiv.innerHTML.trim() !== "") {
        saveButton.disabled = false; // Abilita il bottone
    } else {
        saveButton.disabled = true; // Disabilita il bottone
    }
}

// Chiamare la funzione precedente quando la pagina viene caricata
document.addEventListener('DOMContentLoaded', () => {
    updateSaveCollationButton();
});

async function fetchWithLoading(url, options = {}) {
    // Aggiungi la classe 'loading' al body
    document.body.classList.add('loading');

    try {
        const response = await fetch(url, options);
        return response;
    } finally {
        // Rimuovi la classe 'loading' dal body, indipendentemente dal successo o fallimento
        document.body.classList.remove('loading');
    };
};

// Abilitare la selezione delle celle dei testimoni per accogliere le lezioni
function enableCellSelection() {
    const collationTable = document.getElementById('collationHTMLtable');
    if (!collationTable) return;

    const witnessCells = collationTable.querySelectorAll('td.witness-cell');

    witnessCells.forEach(cell => {
        cell.addEventListener('click', handleCellSelection);
    });
};

// Funzione per gestire la selezione delle celle
function handleCellSelection(event) {
    const clickedCell = event.target;
    const currentRow = clickedCell.parentElement;

    // Se la cella era già selezionata, deselezionarla
    if (clickedCell.classList.contains('selected-cell')) {
        clickedCell.classList.remove('selected-cell');

        return
    };

    // Deseleziona qualsiasi altra cella selezionata nella stessa riga
    const selectedCells = currentRow.querySelectorAll('.selected-cell');
    selectedCells.forEach(cell => cell.classList.remove('selected-cell'));

    // Seleziona la cella cliccata
    clickedCell.classList.add('selected-cell');
};

function updateWitnessesTitle() {
    const witnessTable = document.getElementById('witnesses-table');
    const witnessCount = witnessTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;
    const titleElement = document.getElementById('witness-table-title');

    if (witnessCount === 0) {
        titleElement.textContent = "Testimoni nel Database: nessun Testimone attualmente caricato";
    } else {
        titleElement.textContent = "Testimoni nel Database:";
    };
};

// Esportazione in CSV/XLS
document.getElementById('exportButton').addEventListener('click', function () {
    const table = document.getElementById('collationHTMLtable');
    if (!table) {
        alert('Nessuna tabella da esportare.');
        return;
    }

    // Cicla su tutte le celle della tabella e unisce i testi degli span
    const cells = table.querySelectorAll('td');
    cells.forEach(function(cell) {
        const spans = cell.querySelectorAll('span');
        if (spans.length === 0) {
            return;
        }

        let cellText = '';
        // Unisce i testi di ogni span all'interno della cella
        spans.forEach(function(span) {
            cellText += span.innerText + ' ';
        });
        // Rimuove eventuali spazi extra alla fine
        if (cellText) {
            cell.innerText = cellText.trim();
        }
    });

    // Converte un colore CSS rgb()/rgba() nel formato ARGB usato da Excel.
    function excelColor(cssColor) {
        const colorParts = cssColor.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/);
        if (!colorParts || (colorParts[4] !== undefined && Number(colorParts[4]) === 0)) {
            return null;
        }

        return (`FF${Number(colorParts[1]).toString(16).padStart(2, '0')}`
            + `${Number(colorParts[2]).toString(16).padStart(2, '0')}`
            + `${Number(colorParts[3]).toString(16).padStart(2, '0')}`).toUpperCase();
    }

    const collationTable = table.querySelector('#the-collation-table');

    // Converte la tabella HTML in un foglio di calcolo
    const wb = XLSX.utils.table_to_book(
        collationTable,
        { sheet: "Collation Data", raw: true }
    );

    const worksheet = wb.Sheets['Collation Data'];
    Array.from(collationTable.rows).forEach(function (htmlRow, rowIndex) {
        Array.from(htmlRow.cells).forEach(function (htmlCell, columnIndex) {
            const excelCell = worksheet[XLSX.utils.encode_cell({ r: rowIndex, c: columnIndex })];
            if (!excelCell) {
                return;
            }

            const style = {};
            if (rowIndex === 0) {
                style.font = { bold: true };
            }

            // The category column is always the penultimate column.
            if (columnIndex !== htmlRow.cells.length - 2) {
                style.alignment = { wrapText: true };
            }

            const backgroundColor = excelColor(window.getComputedStyle(htmlCell).backgroundColor);
            if (backgroundColor) {
                style.fill = {
                    patternType: 'solid',
                    fgColor: { rgb: backgroundColor }
                };
            }

            if (Object.keys(style).length > 0) {
                excelCell.s = style;
            }
        });
    });

    // Excel stores sizes per column and per row, not per cell. Calculate them
    // from the exported values to mirror Excel's auto-fit behaviour.
    const exportedRows = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
    const columnWidths = [];
    exportedRows.forEach(function (row) {
        row.forEach(function (value, columnIndex) {
            const longestLine = String(value)
                .split(/\r?\n/)
                .reduce(function (length, line) { return Math.max(length, line.length); }, 0);
            columnWidths[columnIndex] = Math.max(columnWidths[columnIndex] || 0, longestLine);
        });
    });
    worksheet['!cols'] = columnWidths.map(function (width) {
        return { wch: Math.max(1, width + 2) };
    });

    worksheet['!rows'] = exportedRows.map(function (row) {
        const lineCount = row.reduce(function (maximum, value, columnIndex) {
            const columnWidth = Math.max(1, columnWidths[columnIndex] || 1);
            const wrappedLines = String(value).split(/\r?\n/).reduce(function (count, line) {
                return count + Math.max(1, Math.ceil(line.length / columnWidth));
            }, 0);
            return Math.max(maximum, wrappedLines);
        }, 1);
        return { hpt: 15 * lineCount };
    });

    // Genera il file Excel e lo scarica
    XLSX.writeFile(wb, 'collation_export.xlsx');
});


// Funzione per mostrare il modale di cambio password
function showChangePasswordModal() {
    document.getElementById('changePasswordModal').style.display = 'block';
}

// Funzione per chiudere il modale di cambio password
function closeChangePasswordModal() {
    document.getElementById('changePasswordModal').style.display = 'none';
}

// Gestione del form di cambio password
document.getElementById('changePasswordForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (newPassword !== confirmPassword) {
        alert('La nuova password e la conferma non corrispondono.');
        return;
    }

    const response = await fetch('/change_password/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
        }),
    });

    if (response.ok) {
        alert('Password aggiornata con successo!');
        closeChangePasswordModal();
    } else {
        const result = await response.json();
        alert(`Errore: ${result.detail}`);
    }
});

// Chiudi il modale se l'utente clicca fuori di esso
window.onclick = function(event) {
    const modal = document.getElementById('changePasswordModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

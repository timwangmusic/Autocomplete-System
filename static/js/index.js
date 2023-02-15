async function search_words() {
    const searchTerm = document.getElementById("searchTerm").value;
    const results = await (await fetch(`/search?term=${searchTerm}`)).json();

    let resultsList = $('#results')
    resultsList.empty();
    for (const r of results.results) {
        resultsList.append($('<li>').addClass('list-group-item list-group-item-success').text(r));
    }
    await loadSearchHistory();
}

async function loadSearchHistory() {
    const url = '/search_history';
    const obj = await (await fetch(url)).json();

    let search_history = $('#search_history');
    search_history.empty();
    for (const term of obj.result) {
        search_history.append($('<li>').addClass('list-group-item list-group-item-primary').text(term));
    }
}

$('#searchBtn').click(search_words);
$('#searchTerm').on('keypress',
    async (e) => {
        if (e.key === 'Enter') {
            console.log("user starts search");
            await search_words();
        }
    }
);

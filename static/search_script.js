window.onload = function() {

    fetch('/fetch-data', {
        method:'POST', 
        headers: {
        'Content-Type': 'application/json' 
        }, 
        body: JSON.stringify(returnForm)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('No Data Fetched');
        }
        return response.json()})
    .then( data => {
            hideLoadingIndicator();
            updateUI(data);
            }
        )}


function hideLoadingIndicator() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('result_header').style.display = 'block';
}

function updateUI(data) {
    const feedbackContainer = document.querySelector('.feedback')
            const winRateContainer = document.querySelector('.win-rate');
            const matchesContainer = document.querySelector('.outter-outter-div');

            const matches = data.matches;
            const players = data.players;

            if (!data.matches) {
                let playerFound = false

                const feedbackElement = document.createElement("div");
                feedbackElement.classList.add("feedback-container");

                // Create feedback box div
                const feedbackBox = document.createElement("div");
                feedbackBox.classList.add("feedback-box");
                
                if (!data[0].puuid && !data[1].puuid) {
                    console.log(data)
                    feedbackBox.innerHTML = `
                    <div style="display:flex; flex-direction: column">
                        <span class="result-return" style="margin-bottom: 20px;">
                            Sorry,
                        </span>
                        <span class="player-name">"${data[0].name}<span class="player-tag">#${data[0].tag}</span>"</span>
                        <h1>and</h1>
                        <span class="player-name">"${data[1].name}<span class="player-tag">#${data[1].tag}</span>"</span>
                    </div>
                        <span class="result-return" style="margin-top: 20px;">
                            are unregistered summoners.
                        </span>
                    `
                }

                else if (!data[0].puuid) {
                    feedbackBox.innerHTML = `
                    <div style="display:flex; flex-direction: column">
                        <span class="result-return" style="margin-bottom: 20px;">
                            Sorry,
                        </span>
                        <span class="player-name">"${data[0].name}<span class="player-tag">#${data[0].tag}</span>"</span>
                        <span class="result-return" style="margin-top: 20px;">
                            is Not a registered summoner.
                        </span>
                    </div>
                    `
                }

                else if (!data[1].puuid) {
                    feedbackBox.innerHTML = `
                    <div style="display:flex; flex-direction: column">
                        <span class="result-return" style="margin-bottom: 20px;">
                            Sorry,
                        </span>
                        <span class="player-name">"${data[1].name}<span class="player-tag">#${data[1].tag}</span>"</span>
                        <span class="result-return" style="margin-top: 20px;">
                            is Not a registered summoner.
                        </span>
                    </div>
                    `
                }

                else {
                    playerFound = true;
                    
                    feedbackBox.innerHTML = `
                    <div style="display: flex; flex-direction: column;">
                        <span class="player-name">"${data[0].name}<span class="player-tag">#${data[0].tag}</span>"</span>
                        <h1>and</h1>
                        <span class="player-name">"${data[1].name}<span class="player-tag">#${data[1].tag}</span>"</span>
                        <span class="result-return" style="margin-top: 20px;">
                            Have Not played togheter in the past 100 games.
                        </span>
                    </div>
                    `
                }

                const feedbackInstructions = document.createElement("span")
                feedbackInstructions.classList.add("feedback-instructions")

                feedbackInstructions.innerHTML = "Please make sure you have included a #tag line after the Summoner's name.\nAnd make sure you searched the summoner name or region correctly."
                const searchAgainButton = document.createElement("div")
                searchAgainButton.classList.add("search-again")
                searchAgainButton.innerHTML = `
                <form action="/">
                    <div style="display: flex; justify-content: center;">
                        <button class = "btn" type="submit" id="search-again-button">
                        <span class="circle">
                            <i class="fa-solid fa-angle-right"></i>
                        </span>
                        <span class="text">Search Again</span>
                    </div>
                </form>
                `
            
                
                !playerFound && feedbackBox.append(feedbackInstructions);
                feedbackBox.appendChild(searchAgainButton); 


                feedbackElement.appendChild(feedbackBox);
                feedbackContainer.appendChild(feedbackElement);

                
            }
            else {

                matches.forEach(match => {

                    const matchElement = document.createElement("div")
                    win_lose_p1 = `${match.win_lose_p1 ? 'win' : 'lose'}`
                    win_lose_p2 = `${match.win_lose_p2 ? 'win' : 'lose'}`
                    matchElement.classList.add("outter-div", "close")
                    matchElement.innerHTML = `    
                    <div class="row">
                        <div class="col flex-column0 ${win_lose_p1}">
                        </div>
                        <div class="col flex-column1 ${win_lose_p1}">
                            <div class="match-container-left ">
                                <h5 class=${win_lose_p1}>${match.game_mode}</h5>
                                <p>${match.creation_time_ago}</p>
                                <div class="match-win-lose-duration">
                                    
                                    <span>
                                        ${match.duration}
                                    </span>
                                </div>
                                <div class"match-current-rank">

                                </div>
                            </div>
                        </div>
                        <div class="col flex-column2 ${win_lose_p1}">
                            <div class="summ-container">
                                <div class="summ-img-spells">
                                    <dl>
                                        <dt>
                                            <div class="summ-img-container">
                                                <div class="summ-img-ext">
                                                    <div class="summ-img-int">
                                                        <div class="summ-img-lane">
                                                            <div class="summ-img">
                                                                <img class="summ-img-img" src=${match.champ_p1_img} alt=''>
                                                            </div>
                                                            <div class="lane-img">
                                                                <div>
                                                                    <img src="">
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>    
                                        </dt>
                                        <dd>
                                            <div class="summ-spell">
                                                <div class="summ-spell-img-container">
                                                    <img src=${match.spell_1_p1_img}>
                                                </div>
                                            </div>
                                            <div class="summ-spell" style="margin-top: 4px;">
                                                <div class="summ-spell-img-container">
                                                    <img src=${match.spell_2_p1_img}>
                                                </div>
                                            </div>
                                        </dd>
                                        <dd>
                                            <div style="cursor: pointer;">
                                                <div class="rune-img-1-container">
                                                    <div style="position: relative; flex: 1 1 0%;">
                                                        <img src="${match.rune_1_p1_img}">
                                                    </div>
                                                </div>
                                                <div class="rune-img-2-container">
                                                    <div style="position: relative; flex: 1 1 0%;">
                                                        <img src="${match.rune_2_p1_img}">
                                                    </div>
                                                </div>
                                            </div>
                                        </dd>
                                    </dl>
                                    <div class="kda">
                                        <p class="kda-p">
                                            <span>${match.kills_p1}</span>
                                            <span class="slash">/</span>
                                            <span class="span-deaths">${match.deaths_p1}</span>
                                            <span class="slash">/</span>
                                            <span>${match.assists_p1}</span>
                                        </p>
                                        <p class="kda-ratio-p">
                                            <span>${match.kda_p1}</span>
                                        </p>
                                    </div>
                                </div>
                                <div class="items-ward">
                                    <div class="items-ward-container">
                                        <div class="items-ward-inner">${match.items_p1_img.map(item => `
                                                <div class="items">
                                                    <div class="items-inner">
                                                        <img src="${item}" alt="item image" />
                                                    </div>
                                                </div>
                                                `)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col flex-column6 ${win_lose_p2}">
                            <div class="summ-container">
                                <div class="summ-img-spells">
                                    <dl>
                                        <dt>
                                            <div class="summ-img-container">
                                                <div class="summ-img-ext">
                                                    <div class="summ-img-int">
                                                        <div class="summ-img-lane">
                                                            <div class="summ-img">
                                                                <img class="summ-img-img" src=${match.champ_p2_img} alt=''>
                                                            </div>
                                                            <div class="lane-img">
                                                                <div>
                                                                    <img src="">
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>    
                                        </dt>
                                        <dd>
                                            <div class="summ-spell">
                                                <div class="summ-spell-img-container">
                                                    <img src=${match.spell_1_p2_img}>
                                                </div>
                                            </div>
                                            <div class="summ-spell" style="margin-top: 4px;">
                                                <div class="summ-spell-img-container">
                                                    <img src=${match.spell_2_p2_img}>
                                                </div>
                                            </div>
                                        </dd>
                                        <dd>
                                            <div style="cursor: pointer;">
                                                <div class="rune-img-1-container">
                                                    <div style="position: relative; flex: 1 1 0%;">
                                                        <img src="${match.rune_1_p2_img}">
                                                    </div>
                                                </div>
                                                <div class="rune-img-2-container">
                                                    <div style="position: relative; flex: 1 1 0%;">
                                                        <img src="${match.rune_2_p2_img}">
                                                    </div>
                                                </div>
                                            </div>
                                        </dd>
                                    </dl>
                                    <div class="kda">
                                        <p class="kda-p">
                                            <span>${match.kills_p2}</span>
                                            <span class="slash">/</span>
                                            <span class="span-deaths">${match.deaths_p2}</span>
                                            <span class="slash">/</span>
                                            <span>${match.assists_p2}</span>
                                        </p>
                                        <p class="kda-ratio-p">
                                            <span>${match.kda_p2}</span>
                                        </p>
                                    </div>
                                </div>
                                <div class="items-ward">
                                    <div class="items-ward-container">
                                        <div class="items-ward-inner">${match.items_p2_img.map(item => `
                                                <div class="items">
                                                    <div class="items-inner">
                                                        <img src="${item}" alt="item image" />
                                                    </div>
                                                </div>
                                                `)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col flex-column5">
                            
                        </div>
                        <div class="col flex-column7" id="more-match-details">
                            <button>
                                <img src="./static/icon_arrow_lose.svg" alt="Detail">
                            </button>
                        </div>
                    </div>
                `;
                matchesContainer.appendChild(matchElement);

                const clickableRow = matchElement.querySelector('.flex-column7');
                clickableRow.addEventListener("click", function() {
                    toggleMatchDetails(match, matchElement)
                })

                })
            }
}

function toggleMatchDetails(match, matchElement) {
    let detailsDiv = matchElement.nextElementSibling;
    if (detailsDiv && detailsDiv.classList.contains("match-details")) {
        detailsDiv.style.display = detailsDiv.style.display === "none" ? "block" : "none";
    } else {
        detailsDiv = document.createElement("div");
        detailsDiv.classList.add("match-details");
        detailsDiv.innerHTML = `
            <div class="details-container">
                <div style="flex: 1 1 0%">
                    <div style="display: flex; flex-direction: column;>
                        <table class="match-team"></table>
                        <table class="match-team"></table>
                    </div>
                </div>
            </div>
            <div class="match-link"></div>
        `
        matchElement.parentNode.insertBefore(detailsDiv, matchElement.nextSibling);
    }
}
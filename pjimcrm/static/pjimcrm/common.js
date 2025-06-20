function updateTimerDisplay() {
    document.querySelectorAll('.timerMain').forEach(timerEl => {
        let timerData = JSON.parse(timerEl.dataset.timer);
        if(timerData && timerData.running && timerData.timer && timerData.timer.timestamp_started)
        {
            timerEl.dataset.running = "true";
            let startedTimestamp = new Date(timerData.timer.timestamp_started)
            let currentDiff = (new Date() - startedTimestamp) / 1000
            let oldDiff = 0;
            if(timerData.timer.length_raw)
            {
                oldDiff = timerData.timer.length_raw;
            }
            let totalDiff = currentDiff + oldDiff;

            let timerClient = timerEl.querySelector('.timerClientName');
            let timerProject = timerEl.querySelector('.timerProjectName');

            timerClient.innerHTML = timerData.timer.client_name;
            timerProject.innerHTML = timerData.timer.project_name;

            let diffHours = Math.floor(totalDiff / (60*60));
            let diffRemainder = totalDiff % (60*60);
            let diffMinutes = Math.floor(diffRemainder / 60);
            let diffSeconds = Math.floor(diffRemainder % 60);

            let hoursEl = timerEl.querySelector(".timerDisplayHours")
            let minutesEl = timerEl.querySelector(".timerDisplayMinutes")
            let secondsEl = timerEl.querySelector(".timerDisplaySeconds")

            hoursEl.innerText = (diffHours < 10 ? "0" : "") + diffHours.toFixed(0);
            minutesEl.innerText = (diffMinutes < 10 ? "0" : "") + diffMinutes.toFixed(0);
            secondsEl.innerText = (diffSeconds < 10 ? "0" : "") + diffSeconds.toFixed(0);

            let idFieldEl = timerEl.querySelector('input[name=id]');
            idFieldEl.value = timerData.timer.id;
        }
        else {
            timerEl.dataset.running = "false";

        }
        //console.log({timerData, timer: timerData.timer, timestampStarted: timerData.timer.timestamp_started});
    })
}

function updateBannerTimerDisplay() {
    document.querySelectorAll('.timerRunningBanner').forEach(timerEl => {
        if(!timerEl.dataset.timer)
        {
            return;
        }

        let timerData = JSON.parse(timerEl.dataset.timer);
        let timerHeading = timerEl.querySelector(".runningTimerHeading");
        let timerSubheading = timerEl.querySelector(".runningTimerSubheading");
        if(timerData && timerData.running && timerData.timer && timerData.timer.timestamp_started)
        {
            timerEl.dataset.running = "true";
            let startedTimestamp = new Date(timerData.timer.timestamp_started)
            let currentDiff = (new Date() - startedTimestamp) / 1000
            let oldDiff = 0;
            if(timerData.timer.length_raw)
            {
                oldDiff = timerData.timer.length_raw;
            }
            let totalDiff = currentDiff + oldDiff;
            
            if(timerHeading && timerSubheading)
            {
                if(timerData.timer.description_set)
                {
                    timerHeading.innerHTML = timerData.timer.description;
                    timerSubheading.innerHTML = timerData.timer.project_name + ' - ' + timerData.timer.client_name;
                }
                else
                {
                    timerHeading.innerHTML = timerData.timer.project_name;
                    timerSubheading.innerHTML = timerData.timer.client_name;
                }
            }

            let diffHours = Math.floor(totalDiff / (60*60));
            let diffRemainder = totalDiff % (60*60);
            let diffMinutes = Math.floor(diffRemainder / 60);
            let diffSeconds = Math.floor(diffRemainder % 60);

            let hoursEl = timerEl.querySelector(".timerDisplayHours")
            let minutesEl = timerEl.querySelector(".timerDisplayMinutes")
            let secondsEl = timerEl.querySelector(".timerDisplaySeconds")

            hoursEl.innerText = (diffHours < 10 ? "0" : "") + diffHours.toFixed(0);
            minutesEl.innerText = (diffMinutes < 10 ? "0" : "") + diffMinutes.toFixed(0);
            secondsEl.innerText = (diffSeconds < 10 ? "0" : "") + diffSeconds.toFixed(0);

            let idFieldEl = timerEl.querySelector('input[name=id]');
            idFieldEl.value = timerData.timer.id;

            document.querySelectorAll(".disableOnRunning").forEach(targetEl => {
                targetEl.disabled = true;
            });
        }
        else {
            timerEl.dataset.running = "false";
            timerHeading.innerHTML = "";
            timerSubheading.innerHTML = "";

            document.querySelectorAll(".disableOnRunning").forEach(targetEl => {
                targetEl.disabled = false;
            });
        }
        //console.log({timerData, timer: timerData.timer, timestampStarted: timerData.timer.timestamp_started});
    })
}

function fetchBannerTimerData(initUrl) {
    return fetch(initUrl).then(timerData => {
        timerData.text().then(timerDataText => {
            document.querySelectorAll('.timerRunningBanner').forEach(timerEl => {
                timerEl.dataset.timer = timerDataText;
            });
        });
    });

}

function initBannerTimerDisplay(initUrl) {
    if(!document.runningBannerTimerDisplayUpdate)
    {
        document.runningBannerTimerDisplayUpdate = true;
        fetchBannerTimerData(initUrl).then(updateBannerTimerDisplay());
        setInterval(updateBannerTimerDisplay, 200);
        //setInterval(() => { fetchBannerTimerData(initUrl) }, 20000);
    }

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleUpdateTimerDescription(timerEl, event, targetUrl)
{
    const csrftoken = getCookie('csrftoken');

    let descriptionEl = timerEl.querySelector("#timerRunningDescription");

    event.preventDefault();

    let timerData = JSON.parse(timerEl.dataset.timer);
    if(timerData && timerData.timer)
    {
        let descriptionData = new FormData();
        descriptionData.append('id', timerData.timer.id);
        descriptionData.append('description', descriptionEl.value);

        let currentButton = event.currentTarget;

        const request = new Request(
            targetUrl,
            {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                mode: 'same-origin', // Do not send CSRF token to another domain.
                body: descriptionData
            }
        );
        event.currentTarget.disabled = true;
        fetch(request).then(function(response) {
            // ...
        })
        .finally(() => {
            currentButton.disabled = false;
        });
    }

    return false;
}

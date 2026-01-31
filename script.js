document.getElementById('getWeather').addEventListener('click', function() {
    const city = document.getElementById('city').value;
    const apiKey = '141623457ed8473b88b145446242110';
    const url = `https://api.weatherapi.com/v1/current.json?key=${apiKey}&q=${city}&aqi=no`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('City not found');
            }
            return response.json();
        })
        .then(data => {
            const weatherDescription = data.current.condition.text;
            const temperature = data.current.temp_c;
            const result = `
                <h2>Weather in ${data.location.name}, ${data.location.country}</h2>
                <p>Temperature: ${temperature} °C</p>
                <p>Description: ${weatherDescription}</p>
            `;
            document.getElementById('weatherResult').innerHTML = result;
        })
        .catch(error => {
            document.getElementById('weatherResult').innerHTML = `<p style="color: red;">${error.message}</p>`;
        });
});
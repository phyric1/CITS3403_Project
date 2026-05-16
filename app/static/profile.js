const statLabels = {
    score: "Score",
    turns: "Turns",
    gold: "Gold Collected",
    enemies: "Enemies Defeated",
    movement: "Movement Cards Used",
    survival: "Survival Cards Used",
    combat: "Combat Cards Used",
    utility: "Utility Cards Used"
};

let currentStat = "score";

document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("gameChart");

  const chart = new Chart(ctx, {
      type: "line",
      data: {
          labels: window.gameData.labels,
          datasets: [{
              label: statLabels[currentStat],
              data: window.gameData[currentStat],
              borderWidth: 2,
              tension: 0.3,
              fill: true
          }]
      },
      options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
              mode: "index",
              intersect: false
          },
          scales: {
              y: {
                  beginAtZero: true
              }
          },
          scales: {
              y: {
                  title: {
                      display: true,
                      text: statLabels[currentStat]
                  },
                  beginAtZero: true,
                  min: 0
              },
              x: {
                  title: {
                      display: true,
                      text: "Last 10 Games"
                  }
              }
          },
          plugins: {
              tooltip: {
                  callbacks: {
                      label: function(context) {
                          const i = context.dataIndex;
                          const win = window.gameData.wins[i];
                          const diff = window.gameData.difficulty[i];
                          const diffText = ["Easy", "Normal", "Hard"][diff];
                          return [
                              `Score: ${context.parsed.y}`,
                              win ? "Win" : "Loss",
                              `Difficulty: ${diffText}`
                          ];
                      }
                  }
            },
            legend: {
                    display: false
            }
          }
      },
  });

  document.getElementById("statSelect").addEventListener("change", (e) => {
      currentStat = e.target.value;
      chart.data.datasets[0].label = statLabels[currentStat];
      chart.data.datasets[0].data = window.gameData[currentStat];
      chart.update();
  });
});

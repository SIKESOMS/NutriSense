import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip } from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip);

const labels = ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Iron", "Calcium", "Vitamin C"];
const keys = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "iron_mg", "calcium_mg", "vitamin_c_mg"];

export default function NutritionChart({ nutrition }) {
  if (!nutrition || typeof nutrition !== "object") return null;
  const values = keys.map((key) => Number(nutrition[key]) || 0);
  return (
    <section className="nutrition-card">
      <div className="section-heading"><div><p className="eyebrow">Meal analysis</p><h2>Nutrient totals</h2></div></div>
      <div className="chart-wrap">
        <Bar
          data={{ labels, datasets: [{ data: values, backgroundColor: ["#f59e0b", "#2f7d4a", "#72b67d", "#e69a44", "#518c5b", "#d97706", "#3f8f73", "#f4bd51"], borderRadius: 8, borderSkipped: false }] }}
          options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (context) => `${context.raw}` } } }, scales: { x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 45 } }, y: { beginAtZero: true, grid: { color: "#edf3ec" } } } }}
        />
      </div>
      <div className="nutrition-summary">
        {keys.map((key, index) => <span key={key}><b>{values[index]}</b> {key === "calories" ? "kcal" : key.endsWith("_mg") ? "mg" : "g"}</span>)}
      </div>
    </section>
  );
}

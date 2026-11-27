import type { components } from "../../../api/schema";
import { formatAnalysisCategory } from "../../../presentation";
import { Card } from "../../ui/Card/Card";
import { Icon } from "../../ui/Icon/Icon";
import styles from "./AnalysisPanel.module.css";

type Analysis = components["schemas"]["Analysis"];
type AnalysisCategory = components["schemas"]["AnalysisCategory"];

const categories: AnalysisCategory[] = [
  "vocabulary",
  "grammar",
  "errors_corrections",
  "reinforced_successes",
  "key_concepts",
  "resolved_questions"
];

interface AnalysisPanelProps {
  analysis: Analysis;
}

function CategorySection({ category, items }: { category: AnalysisCategory; items: Analysis["items"] }) {
  const title = formatAnalysisCategory(category);
  const titleId = `analysis-category-${category}`;

  return <section className={styles.category} aria-labelledby={titleId}>
    <h3 id={titleId}>{title}</h3>
    {items.length > 0
      ? <ul>{items.map((item) => <li key={item.item_id}>{item.content}</li>)}</ul>
      : <p className={styles.empty}>Sin elementos identificados en esta categoría.</p>}
  </section>;
}

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  const isEmpty = !analysis.general_summary.trim() && analysis.items.length === 0;

  return <Card aria-labelledby="analysis-title" className={styles.panel}>
    <h2 id="analysis-title"><Icon name="check" />Repaso pedagógico</h2>
    {isEmpty && <p className={styles.allEmpty}>El repaso pedagógico todavía no contiene elementos para esta clase.</p>}
    <section className={styles.summary} aria-labelledby="analysis-summary-title">
      <p className="eyebrow">Visión general</p>
      <h3 id="analysis-summary-title">Resumen de la clase</h3>
      <p>{analysis.general_summary.trim() || "No hay resumen general disponible para esta clase."}</p>
    </section>
    <div className={styles.categoryGrid}>
      {categories.map((category) => <CategorySection category={category} items={analysis.items.filter((item) => item.category === category)} key={category} />)}
    </div>
  </Card>;
}

/*
 * GestionPro - logique cote navigateur.
 * Ce script dialogue avec l'API REST (/api) pour afficher, creer,
 * modifier et supprimer des taches, et pour alimenter le tableau de bord.
 */

const API = "/api";

// References vers les elements du formulaire
const form = document.getElementById("form-tache");
const champId = document.getElementById("tache-id");
const titreForm = document.getElementById("titre-form");
const btnValider = document.getElementById("btn-valider");
const btnAnnuler = document.getElementById("btn-annuler");

let graphStatut = null;
let graphPriorite = null;

// ---------- Chargement et affichage des taches ----------

async function chargerTaches() {
  const filtre = document.getElementById("filtre-statut").value;
  const url = filtre ? `${API}/taches?statut=${encodeURIComponent(filtre)}` : `${API}/taches`;
  const reponse = await fetch(url);
  const taches = await reponse.json();
  afficherTaches(taches);
}

function afficherTaches(taches) {
  const recherche = document.getElementById("recherche").value.toLowerCase();
  const corps = document.getElementById("corps-tableau");
  corps.innerHTML = "";

  // Filtre de recherche cote client (sur le titre et le responsable)
  const filtrees = taches.filter(t =>
    t.titre.toLowerCase().includes(recherche) ||
    (t.responsable || "").toLowerCase().includes(recherche)
  );

  document.getElementById("message-vide").hidden = filtrees.length > 0;

  for (const t of filtrees) {
    const classeStatut = "statut-" + t.statut.toLowerCase().replace(/\s+/g, "");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${echapper(t.titre)}</td>
      <td>${echapper(t.responsable || "-")}</td>
      <td><span class="badge ${classeStatut}">${t.statut}</span></td>
      <td class="prio-${t.priorite}">${t.priorite}</td>
      <td><span class="barre-avancement"><span style="width:${t.avancement}%"></span></span> ${t.avancement}%</td>
      <td>${t.date_echeance || "-"}</td>
      <td>
        <button class="btn-icone" title="Modifier" data-edit="${t.id}">✏️</button>
        <button class="btn-icone" title="Supprimer" data-del="${t.id}">🗑️</button>
      </td>`;
    corps.appendChild(tr);
  }

  // Branchement des boutons modifier / supprimer
  corps.querySelectorAll("[data-edit]").forEach(b =>
    b.addEventListener("click", () => preparerModification(b.dataset.edit)));
  corps.querySelectorAll("[data-del]").forEach(b =>
    b.addEventListener("click", () => supprimerTache(b.dataset.del)));
}

// ---------- Tableau de bord (KPI + graphiques) ----------

async function chargerStats() {
  const reponse = await fetch(`${API}/stats`);
  const s = await reponse.json();

  document.getElementById("kpi-total").textContent = s.total;
  document.getElementById("kpi-terminees").textContent = s.terminees;
  document.getElementById("kpi-completion").textContent = s.taux_completion + "%";
  document.getElementById("kpi-avancement").textContent = s.avancement_moyen + "%";

  dessinerGraphStatut(s.par_statut);
  dessinerGraphPriorite(s.par_priorite);
}

function dessinerGraphStatut(parStatut) {
  const ctx = document.getElementById("graph-statut");
  if (graphStatut) graphStatut.destroy();
  graphStatut = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(parStatut),
      datasets: [{ data: Object.values(parStatut), backgroundColor: ["#e07a5f", "#e0a03c", "#1b7a45"] }],
    },
    options: { plugins: { legend: { position: "bottom" } } },
  });
}

function dessinerGraphPriorite(parPriorite) {
  const ctx = document.getElementById("graph-priorite");
  if (graphPriorite) graphPriorite.destroy();
  graphPriorite = new Chart(ctx, {
    type: "bar",
    data: {
      labels: Object.keys(parPriorite),
      datasets: [{ label: "Tâches", data: Object.values(parPriorite), backgroundColor: "#1b7fa8" }],
    },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
  });
}

// ---------- Creation / modification / suppression ----------

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const donnees = {
    titre: document.getElementById("f-titre").value,
    responsable: document.getElementById("f-responsable").value,
    statut: document.getElementById("f-statut").value,
    priorite: document.getElementById("f-priorite").value,
    avancement: document.getElementById("f-avancement").value,
    date_echeance: document.getElementById("f-echeance").value || null,
  };

  const id = champId.value;
  if (id) {
    await fetch(`${API}/taches/${id}`, methodeJson("PUT", donnees));
  } else {
    await fetch(`${API}/taches`, methodeJson("POST", donnees));
  }
  reinitialiserFormulaire();
  rafraichir();
});

async function preparerModification(id) {
  const reponse = await fetch(`${API}/taches/${id}`);
  const t = await reponse.json();
  champId.value = t.id;
  document.getElementById("f-titre").value = t.titre;
  document.getElementById("f-responsable").value = t.responsable;
  document.getElementById("f-statut").value = t.statut;
  document.getElementById("f-priorite").value = t.priorite;
  document.getElementById("f-avancement").value = t.avancement;
  document.getElementById("f-echeance").value = t.date_echeance || "";
  titreForm.textContent = "Modifier la tâche";
  btnValider.textContent = "Enregistrer";
  btnAnnuler.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function supprimerTache(id) {
  if (!confirm("Supprimer cette tâche ?")) return;
  await fetch(`${API}/taches/${id}`, { method: "DELETE" });
  rafraichir();
}

btnAnnuler.addEventListener("click", reinitialiserFormulaire);

function reinitialiserFormulaire() {
  form.reset();
  champId.value = "";
  titreForm.textContent = "Ajouter une tâche";
  btnValider.textContent = "Ajouter";
  btnAnnuler.hidden = true;
}

// ---------- Utilitaires ----------

function methodeJson(methode, donnees) {
  return { method: methode, headers: { "Content-Type": "application/json" }, body: JSON.stringify(donnees) };
}

function echapper(texte) {
  const div = document.createElement("div");
  div.textContent = texte;
  return div.innerHTML;
}

function rafraichir() {
  chargerTaches();
  chargerStats();
}

// Rechargements declenches par les filtres
document.getElementById("recherche").addEventListener("input", chargerTaches);
document.getElementById("filtre-statut").addEventListener("change", chargerTaches);

// Premier chargement
rafraichir();

const surahSelect = document.getElementById("surahSelect");
const statusEl = document.getElementById("status");
const ayahContainer = document.getElementById("ayahContainer");
const ayahTemplate = document.getElementById("ayahTemplate");
const tooltip = document.getElementById("tooltip");
const quranFontSelect = document.getElementById("quranFontSelect");
const translationFontSelect = document.getElementById("translationFontSelect");

const API_BASE = "https://api.alquran.cloud/v1";
const wordLexicon = {
  الله: "خداوند",
  الرحمن: "بسیار مهربان",
  الرحيم: "مهربان همیشگی",
  رب: "پروردگار",
  العالمين: "جهانیان",
  الدين: "روز جزا",
  اهدنا: "هدایت کن ما را",
  الصراط: "راه",
  المستقيم: "راست و مستقیم",
};

const hadithProviders = [
  {
    source: "alvahy.com",
    buildUrl: (surah, ayah) =>
      `https://www.alvahy.com/api/hadith?surah=${surah}&ayah=${ayah}`,
  },
  {
    source: "quran.inoor.ir",
    buildUrl: (surah, ayah) =>
      `https://quran.inoor.ir/fa/api/hadith?surah=${surah}&ayah=${ayah}`,
  },
];

const updateFonts = () => {
  document.documentElement.style.setProperty("--quran-font", `"${quranFontSelect.value}", serif`);
  document.documentElement.style.setProperty(
    "--translation-font",
    `"${translationFontSelect.value}", sans-serif`
  );
};

async function loadSurahs() {
  const response = await fetch(`${API_BASE}/surah`);
  const payload = await response.json();
  payload.data.forEach((surah) => {
    const option = document.createElement("option");
    option.value = surah.number;
    option.textContent = `${surah.number}. ${surah.name} - ${surah.englishName}`;
    surahSelect.append(option);
  });
}

function createArabicWords(text) {
  return text
    .trim()
    .split(/\s+/)
    .map((word) => {
      const cleanWord = word.replace(/[\u06D6-\u06ED،؛.]/g, "");
      return `<span class="ayah-word" data-word="${cleanWord}">${word}</span>`;
    })
    .join(" ");
}

async function fetchHadithForAyah(surah, ayah) {
  const collected = [];

  await Promise.all(
    hadithProviders.map(async (provider) => {
      const url = provider.buildUrl(surah, ayah);
      try {
        const response = await fetch(url);
        if (!response.ok) return;
        const data = await response.json();
        const items = Array.isArray(data?.data) ? data.data : Array.isArray(data) ? data : [];
        items.slice(0, 3).forEach((item) => {
          collected.push({
            text: item.text || item.hadith || "حدیث بدون متن",
            source: provider.source,
            url: item.url || url,
          });
        });
      } catch (_error) {
        // اگر API مقصد در دسترس نبود، از منبع بعدی ادامه می‌دهیم
      }
    })
  );

  return collected;
}

async function renderSurah(surahNumber) {
  statusEl.textContent = "در حال دریافت آیات و ترجمه...";
  ayahContainer.innerHTML = "";

  try {
    const [arabicResp, faResp] = await Promise.all([
      fetch(`${API_BASE}/surah/${surahNumber}/ar.alafasy`),
      fetch(`${API_BASE}/surah/${surahNumber}/fa.fooladvand`),
    ]);

    const arabic = await arabicResp.json();
    const persian = await faResp.json();

    arabic.data.ayahs.forEach((ayah, index) => {
      const node = ayahTemplate.content.firstElementChild.cloneNode(true);
      node.querySelector(".ayah-number").textContent = ayah.numberInSurah;
      node.querySelector(".ayah-arabic").innerHTML = createArabicWords(ayah.text);
      node.querySelector(".ayah-translation").textContent = persian.data.ayahs[index]?.text || "";

      const hadithScroll = node.querySelector(".hadith-scroll");
      hadithScroll.innerHTML = "<small>در حال واکشی احادیث از alvahy.com و quran.inoor.ir ...</small>";

      fetchHadithForAyah(surahNumber, ayah.numberInSurah).then((hadiths) => {
        hadithScroll.innerHTML = "";
        if (!hadiths.length) {
          hadithScroll.innerHTML =
            "<small>برای این آیه حدیثی از منابع آنلاین یافت نشد یا دسترسی API محدود است.</small>";
          return;
        }

        hadiths.forEach((hadith) => {
          const item = document.createElement("article");
          item.className = "hadith-item";
          item.innerHTML = `
            <div>${hadith.text}</div>
            <span class="hadith-meta">منبع: ${hadith.source} | آدرس: <a href="${hadith.url}" target="_blank" rel="noopener noreferrer">${hadith.url}</a></span>
          `;
          hadithScroll.append(item);
        });
      });

      ayahContainer.append(node);
    });

    statusEl.textContent = "";
  } catch (error) {
    statusEl.textContent = `خطا در بارگذاری سوره: ${error.message}`;
  }
}

ayahContainer.addEventListener("mousemove", (event) => {
  const wordEl = event.target.closest(".ayah-word");
  if (!wordEl) {
    tooltip.classList.remove("visible");
    return;
  }

  const word = wordEl.dataset.word;
  const meaning = wordLexicon[word] || "معنی لغوی این واژه در واژه‌نامه محلی ثبت نشده است.";
  tooltip.textContent = `${word}: ${meaning}`;
  tooltip.style.left = `${event.clientX - 130}px`;
  tooltip.style.top = `${event.clientY - 48}px`;
  tooltip.classList.add("visible");
});

ayahContainer.addEventListener("mouseleave", () => tooltip.classList.remove("visible"));

surahSelect.addEventListener("change", () => renderSurah(surahSelect.value));
quranFontSelect.addEventListener("change", updateFonts);
translationFontSelect.addEventListener("change", updateFonts);

(async function init() {
  updateFonts();
  try {
    await loadSurahs();
    statusEl.textContent = "";
    surahSelect.value = "1";
    renderSurah(1);
  } catch (error) {
    statusEl.textContent = `خطا در دریافت سوره‌ها: ${error.message}`;
  }
})();

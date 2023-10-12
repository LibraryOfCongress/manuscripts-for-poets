class App {
  constructor(options = {}) {
    const defaults = {
      maxWordsDisplay: 1000,
      project: 'mary-church-terrell',
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    this.$main = $('.main-content').first();
    this.$timeline = $('.timeline').first();
    this.$words = $('.words').first();

    const timelineDataURL = `../data/${this.options.project}/cloud.json`;
    const timelineDataPromise = $.getJSON(timelineDataURL, (data) => data);

    const transcriptDataURL = `../data/${this.options.project}/transcripts.json`;
    const transcriptDataPromise = $.getJSON(transcriptDataURL, (data) => data);
    this.transcriptDataPromise = $.Deferred();

    $.when(timelineDataPromise).done((data) => {
      this.onCloudDataLoad(data);
    });

    $.when(transcriptDataPromise).done((data) => {
      this.onTranscriptDataLoad(data);
      this.transcriptDataPromise.resolve();
    });
  }

  filterData() {
    const { words } = this;
    const selected = {};

    this.facets.forEach((facet) => {
      const $el = $(`#input-${facet.id}`);
      const value = parseInt($el.val(), 10);
      if ('indexIsValue' in facet && facet.indexIsValue) selected[facet.id] = value;
      else selected[facet.id] = value >= 0 ? facet.values[value] : false;
    });

    selected.year = -1;
    if ($('.timeline .year.selected').length > 0) {
      selected.year = parseInt($('.timeline .year.selected').attr('data-year'), 10);
    }

    let buckets = this.wordBuckets.slice();
    // filter out years
    if (selected.year >= 0) buckets = buckets.filter((b) => b.year === selected.year);
    // filter out subcollections
    if (selected.subCollection >= 0) {
      buckets = buckets.filter((b) => b.subcollectionIndex === selected.subCollection);
    }
    // filter out parts of speech
    if (selected.partOfSpeech !== false) {
      buckets = buckets.filter((b) => {
        const partOfSpeech = this.partsOfSpeech[words[b.wordIndex].pos];
        return partOfSpeech === selected.partOfSpeech;
      });
    }
    // // filter out sentiment
    // if (selected.sentiment >= 0) {
    //   const sentimentFacet = _.find(this.facets, (f) => f.id === 'sentiment');
    //   const sentimentCount = sentimentFacet.values.length;
    //   const sentimentStep = 1.0 / sentimentCount;
    //   const minValue = selected.sentiment * sentimentStep;
    //   const maxValue = minValue + sentimentStep;
    //   buckets = buckets.filter((b) => {
    //     const sentiment = words[b.wordIndex];
    //     return sentiment >= minValue && sentiment <= maxValue;
    //   });
    // }
    this.filteredWords = _.sortBy(buckets, (b) => -b.count);
  }

  loadListeners() {
    $('.start').on('click', (e) => {
      $('.app').addClass('active');
      $('.intro').removeClass('active');
    });

    this.$main.on('change', '.facet', (e) => {
      this.filterData();
      this.renderTimeline();
      this.renderWords();
    });

    // this.$timeline.on('click', '.year', (e) => {
    //   const $target = $(e.currentTarget);
    //   this.onClickYear($target);
    // });
  }

  onClickYear($target) {
    if ($target.hasClass('selected')) $target.removeClass('selected');
    else {
      $('.year').removeClass('selected');
      $target.addClass('selected');
    }
    this.filterData();
    this.renderTimeline();
    this.renderWords();
  }

  onCloudDataLoad(data) {
    console.log('Coud data loaded.');

    this.words = DataUtil.loadCollectionFromRows(data.words, false, true);
    this.wordBuckets = DataUtil.loadCollectionFromRows(data.wordBuckets, false, true);
    this.wordDocs = _.chunk(data.wordDocs, 2);
    this.timeRange = data.timeRange;
    this.partsOfSpeech = _.object(data.partsOfSpeech);

    this.facets = [];
    this.facets.push({
      id: 'subCollection',
      label: 'Sub-collection',
      type: 'select',
      values: data.subCollections,
      indexIsValue: true,
    });
    this.facets.push({
      id: 'partOfSpeech',
      label: 'Part of speech',
      type: 'select',
      values: data.partsOfSpeech.map((d) => d[1]),
      valueType: 'tuple',
    });
    // this.facets.push({
    //   id: 'sentiment',
    //   label: 'Sentiment',
    //   type: 'select',
    //   values: [
    //     'Very negative',
    //     'Negative',
    //     'Neutral',
    //     'Positive',
    //     'Very positive',
    //   ],
    // });
    this.cloudDataLoaded = true;

    this.renderFacets();
    this.filterData();
    this.renderTimeline();
    this.renderWords();
    this.$main.removeClass('is-loading');
    this.loadListeners();
  }

  onTranscriptDataLoad(transcriptData) {
    this.documents = DataUtil.loadCollectionFromRows(transcriptData, (doc) => {
      const updatedDoc = doc;
      updatedDoc.id = doc.index;
      updatedDoc.itemUrl = `https://www.loc.gov/resource/${doc.ResourceID}/?sp=${doc.ItemAssetIndex}&st=text`;
      return updatedDoc;
    });
    console.log('Transcript data loaded.');
    this.transcriptsLoaded = true;
  }

  renderFacets() {
    const { facets } = this;
    let html = '';

    facets.forEach((facet) => {
      html += `<label for="input-${facet.id}">${facet.label}</label>`;
      if (facet.type === 'select') {
        html += `<select id="input-${facet.id}" name="${facet.id}" class="facet">`;
        html += '<option value="-1">Any</option>';
        facet.values.forEach((value, index) => {
          html += `<option value="${index}">${value}</option>`;
        });
        html += '</select>';
      }
    });

    $('.facets').first().html(html);
  }

  renderTimeline() {
    const { $timeline, filteredWords } = this;
    const [startYear, endYear] = this.timeRange;
    const yearCount = endYear - startYear + 1;
    const yearWidth = (1.0 / yearCount) * 100;
    const dataGroups = _.groupBy(filteredWords, 'year');
    const counts = _.map(dataGroups, (group) => group.length);
    const minCount = _.min(counts);
    const maxCount = _.max(counts);
    let html = '';
    for (let year = startYear; year <= endYear; year += 1) {
      const i = year - startYear;
      const left = i * yearWidth;
      let yearHeight = 0;
      let count = 0;
      if (_.has(dataGroups, year)) {
        count = dataGroups[year].length;
        const n = MathUtil.norm(count, minCount, maxCount);
        yearHeight = MathUtil.lerp(0.25, 0.72, n) * 100;
        html += `<button class="year" data-year="${year}" style="width: ${yearWidth}%; height: ${yearHeight}%; left: ${left}%" title="${year} (${count.toLocaleString()} words)">`;
        html += `<span class="visually-hidden">${year} (${count})</span>`;
        html += '</button>';
      }
      if (year % 10 === 0) {
        html += `<div class="year-label" style="left: ${left}%"><div class="text">${year}</div></div>`;
      }
    }
    $timeline.html(html);
  }

  renderWords() {
    const { words, $words } = this;
    const { filteredWords } = this;
    const dataGroups = _.groupBy(filteredWords, 'wordIndex');
    let wordGroups = _.map(dataGroups, (group, wordIndex) => {
      const word = { wordIndex };
      word.count = _.reduce(group, (memo, w) => memo + w.count, 0);
      return word;
    });
    wordGroups = _.sortBy(wordGroups, (g) => -g.count);
    if (wordGroups.length > this.options.maxWordsDisplay) {
      wordGroups = wordGroups.slice(0, this.options.maxWordsDisplay);
    }
    const counts = _.pluck(wordGroups, 'count');
    const minCount = _.min(counts);
    const maxCount = _.max(counts);
    let html = '';
    wordGroups.forEach((wordData) => {
      const word = words[wordData.wordIndex];
      const n = MathUtil.norm(wordData.count, minCount, maxCount);
      const fontSize = MathUtil.lerp(0.667, 3, n);
      html += `<button class="word" data-index="${wordData.wordIndex}" style="font-size: ${fontSize}rem">${word.lemma}</button>`;
    });
    $words.html(html);
  }
}

(function initApp() {
  const app = new App({});
}());

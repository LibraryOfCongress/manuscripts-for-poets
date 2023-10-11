class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
      subCollection0: 2,
      subCollection1: 4,
      wordPad: 10,
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    this.transcriptsLoaded = false;

    // parse templates
    _.templateSettings = {
      interpolate: /\{\{(.+?)\}\}/g,
    };
    this.searchResultItemTemplate = _.template($('#search-result-list-item-template').html());
    this.$results = $('#search-results-list');
    this.$resultsContainer = $('#search-results');
    this.$resultsMessage = $('#search-message');

    const timelineDataURL = `../data/${this.options.project}/timeline.json`;
    const timelineDataPromise = $.getJSON(timelineDataURL, (data) => data);

    const transcriptDataURL = `../data/${this.options.project}/transcripts.json`;
    const transcriptDataPromise = $.getJSON(transcriptDataURL, (data) => data);
    this.transcriptDataPromise = $.Deferred();

    $.when(timelineDataPromise).done((timelineData) => {
      this.onTimelineDataLoad(timelineData);
    });

    $.when(transcriptDataPromise).done((transcriptData) => {
      this.onTranscriptDataLoad(transcriptData);
      this.transcriptDataPromise.resolve();
    });
  }

  filterResults(year, subcollectionIndex) {
    const [yearStart] = this.timelineRange;
    const yearIndex = year - yearStart;
    const subcollection = this.timelineData[subcollectionIndex];
    const { title } = subcollection;
    const docIndices = subcollection.years[yearIndex].docs;
    const count = docIndices.length;

    this.$resultsMessage.html(`Loading <strong>${count}</strong> results from <strong>${year}</strong> within <strong><em>"${title}"</em></strong>`);
    this.$results.html('');
    this.$resultsContainer.addClass('active');

    $.when(this.transcriptDataPromise).done(() => {
      const docs = [];
      docIndices.forEach((docIndex) => {
        docs.push(this.documents[docIndex]);
      });
      this.$resultsMessage.html(`Showing <strong>${count}</strong> results from <strong>${year}</strong> within <strong><em>"${title}"</em></strong>`);
      this.renderDocs(docs);
    });
  }

  loadListeners() {
    const $timeline = $('.timeline').first();
    const [timeline] = $timeline;
    $timeline.on('wheel', (e) => {
      e.preventDefault();
      const { deltaY } = e.originalEvent;
      timeline.scrollLeft += deltaY * 0.667;
    });

    $timeline.on('click', 'button.year', (e) => {
      const $target = $(e.currentTarget);
      const year = parseInt($target.attr('data-year'), 10);
      const subcollection = parseInt($target.attr('data-subcollection'), 10);
      this.filterResults(year, subcollection);
    });

    $('.close-search-results').on('click', (e) => {
      this.$resultsContainer.removeClass('active');
    });
  }

  onTimelineDataLoad(timelineData) {
    console.log('Timeline data loaded.');

    this.timelineData = timelineData.collections;
    this.timelineRange = timelineData.range;
    this.annotations = timelineData.annotations;

    this.renderTimelne();
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

  renderDocs(docs, query = false) {
    let html = '';
    const { wordPad } = this.options;
    docs.forEach((document, i) => {
      const text = document.Transcription;
      let matchText = '';
      if (query !== false) {
        matchText = StringUtil.getHighlightedText(text, query, wordPad, wordPad);
      } else {
        matchText = text.trim().split(' ').slice(0, wordPad * 2).join(' ');
      }
      const data = {
        className: '',
        id: document.id,
        matchText,
        sequence: i + 1,
        title: document.Item,
        url: document.itemUrl,
      };
      html += this.searchResultItemTemplate(data);
    });
    this.$results.html(html);
  }

  renderTimelne() {
    const { timelineData, annotations } = this;
    const [yearStart, yearEnd] = this.timelineRange;
    let labelsHTML = '';
    let timelineHTML = '';
    let yearsHTML = '';
    let notesHTML = '';
    const yearCount = yearEnd - yearStart + 1;

    _.times(yearCount, (j) => {
      const year = yearStart + j;
      yearsHTML += `<div class="year">${year}</div>`;
    });

    annotations.forEach((note) => {
      const { dateStart, dateEnd, event } = note;
      const delta = dateEnd - dateStart;
      const leftN = MathUtil.norm(dateStart + 0.4, yearStart, yearEnd + 1);
      const left = leftN * 100;
      const text = delta > 0 ? `(${dateStart} - ${dateEnd}) ${event}` : `(${dateStart}) ${event}`;
      notesHTML += `<div class="note" style="left: ${left}%">`;
      notesHTML += '<span class="dot"></span>';
      notesHTML += `<span class="text">${text}</span>`;
      notesHTML += '</div>';
    });

    timelineData.forEach((item, i) => {
      const { title, years } = item;
      labelsHTML += '<div class="sub-collection timeline-label">';
      labelsHTML += `<h3>${title}</h3>`;
      labelsHTML += '</div>';

      timelineHTML += '<div class="timeline-row sub-collection">';
      years.forEach((yearData) => {
        const {
          year,
          countN,
          count,
          color,
        } = yearData;
        const textColor = countN > 0.5 ? '#000' : '#fff';
        if (countN <= 0) {
          timelineHTML += '<div class="year"></div>';
        } else {
          timelineHTML += `<button class="year" data-year="${year}" data-subcollection="${i}" style="background: ${color}; color: ${textColor}">${count.toLocaleString()}</button>`;
        }
      });
      timelineHTML += '</div>';
    });

    const $timeline = $('.timeline').first();
    const timelineWidth = yearCount * 40;
    $('.timeline-wrapper').css('width', `${timelineWidth}px`);
    $('.timeline-labels .sub-collections').html(labelsHTML);
    $('.timeline-wrapper .sub-collections').html(timelineHTML);
    $('.timeline-row.years').html(yearsHTML);
    $('.timeline-row.notes').html(notesHTML);
    $timeline[0].scrollLeft = timelineWidth * 0.5 - $timeline.width() * 0.5;
  }
}

(function initApp() {
  const app = new App({});
}());

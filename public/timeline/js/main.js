class App {
  constructor(options = {}) {
    const defaults = {
      project: 'mary-church-terrell',
      subCollection0: 2,
      subCollection1: 4,
    };
    const qparams = StringUtil.queryParams();
    this.options = _.extend({}, defaults, options, qparams);
    this.init();
  }

  init() {
    const timelineDataURL = `../data/${this.options.project}/timeline.json`;
    const timelineDataPromise = $.getJSON(timelineDataURL, (data) => data);

    $.when(timelineDataPromise).done((timelineData) => {
      this.onTimelineDataLoad(timelineData);
    });
  }

  static loadListeners() {
    const $timeline = $('.timeline').first();
    const [timeline] = $timeline;
    $timeline.on('wheel', (e) => {
      e.preventDefault();
      const { deltaY } = e.originalEvent;
      timeline.scrollLeft += deltaY * 0.667;
    });
  }

  onTimelineDataLoad(timelineData) {
    console.log('Timeline data loaded.');

    this.timelineData = timelineData.collections;
    this.timelineRange = timelineData.range;
    this.annotations = timelineData.annotations;

    this.renderTimelne();
    this.constructor.loadListeners();
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
          timelineHTML += '<div class="year">0</div>';
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

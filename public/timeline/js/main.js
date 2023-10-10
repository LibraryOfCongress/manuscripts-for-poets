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
      if (e.originalEvent.deltaY > 0) timeline.scrollLeft += 100;
      else timeline.scrollLeft -= 100;
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

    $('.timeline-wrapper').css('width', `${yearCount * 40}px`);
    $('.timeline-labels .sub-collections').html(labelsHTML);
    $('.timeline-wrapper .sub-collections').html(timelineHTML);
    $('.timeline-row.years').html(yearsHTML);
  }
}

(function initApp() {
  const app = new App({});
}());

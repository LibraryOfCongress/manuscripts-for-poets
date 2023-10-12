class DataUtil {
  static loadCollectionFromRows(data, customMap = false, isFlattened = false) {
    let { rows } = data;
    const { cols, groups } = data;
    if (isFlattened) {
      rows = _.chunk(rows, cols.length);
    }
    const documents = _.map(rows, (row, i) => {
      let doc = _.object(cols, row);
      // parse grouped values
      _.each(groups, (values, field) => {
        doc[field] = values[doc[field]];
      });
      // add additional values
      doc.index = i;
      if (customMap !== false) doc = customMap(doc);
      return doc;
    });
    return documents;
  }
}

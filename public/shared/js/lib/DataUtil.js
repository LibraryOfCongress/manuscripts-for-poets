class DataUtil {
  static loadCollectionFromRows(data, customMap = false) {
    const { rows, cols, groups } = data;
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

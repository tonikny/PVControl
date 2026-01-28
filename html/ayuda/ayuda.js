// const md2html = (mdFile) => {
//   const content = document.getElementById('content');
//   const md = fetch(mdFile)
//     .then((res) => res.text())
//     .then((text) => {
//       console.log('text', text);
//       const converter = new showdown.Converter();
//       const html = converter.makeHtml(text);
//       console.log('html', html);
//       content.innerHTML = html;
//     });
// };

const md2html = async (mdFile) => {
  const content = document.getElementById('content');
  return fetch(mdFile)
    .then((res) => res.text())
    .then((text) => {
      const converter = new showdown.Converter();
      const html = converter.makeHtml(text);
      content.innerHTML = html;
    });
};
// const content = document.getElementById('content');
// const md = fetch('ayuda/index.md')
//   .then((res) => res.text())
//   .then((text) => {
//     const converter = new showdown.Converter();
//     const html = converter.makeHtml(text);
//     content.innerHTML = html;
//   });

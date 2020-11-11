console.log("I am content Script")
const links = document.getElementsByTagName("a");
for (let i = 0; i < links.length; i++) {
    console.log(links.item(i));
    links.item(i).style = "border:1px solid  #999999";
}
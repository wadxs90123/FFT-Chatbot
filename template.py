c3=   {
        "thumbnailImageUrl": "https://example.com/bot/images/item2.jpg",
        "imageBackgroundColor": "#000000",
        "title": "this is menu",
        "text": "description",
        "defaultAction": {
          "type": "uri",
          "label": "View detail",
          "uri": "http://example.com/page/222"
        },
        "actions": [
          {
            "type": "postback",
            "label": "Buy",
            "data": "action=buy&itemid=222"
          },
          {
            "type": "postback",
            "label": "Add to cart",
            "data": "action=add&itemid=222"
          },
          {
            "type": "uri",
            "label": "View detail",
            "uri": "http://example.com/page/222"
          }
        ]
      }
c1 ={
        "thumbnailImageUrl": "https://example.com/bot/images/item1.jpg",
        "imageBackgroundColor": "#FFFFFF",
        "title": "this is menu",
        "text": "description",
        "defaultAction": {
          "type": "uri",
          "label": "View detail",
          "uri": "http://example.com/page/123"
        },
        "actions": [
          {
            "type": "postback",
            "label": "Buy",
            "data": "action=buy&itemid=111"
          },
          {
            "type": "postback",
            "label": "Add to cart",
            "data": "action=add&itemid=111"
          },
          {
            "type": "uri",
            "label": "View detail",
            "uri": "http://example.com/page/111"
          }
        ]
      }
c2= {
        "thumbnailImageUrl": "https://example.com/bot/images/item1.jpg",
        "imageBackgroundColor": "#FFFFFF",
        "title": "this is menu",
        "text": "description",
        "defaultAction": {
          "type": "uri",
          "label": "View detail",
          "uri": "http://example.com/page/123"
        },
        "actions": [
          {
            "type": "postback",
            "label": "Buy",
            "data": "action=buy&itemid=111"
          },
          {
            "type": "postback",
            "label": "Add to cart",
            "data": "action=add&itemid=111"
          },
          {
            "type": "uri",
            "label": "View detail",
            "uri": "http://example.com/page/111"
          }
        ]
      }
carousel=[
{
  "type": "template",
  "altText": "this is a carousel template",
  "template": {
    "type": "carousel",
    "columns": [c1,c1,c1,c1,c2,c2,c3,c3,c3,c3],
    "imageAspectRatio": "rectangle",
    "imageSize": "cover"
  }
},
]
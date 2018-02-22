#// CURRENT:
#// list of topics by {TOPIC:[["TITLE", "URL"]]}
#
#// FUTURE:
#////list of topics by {TOPIC:[["TITLE", "URL", "TAGS"],
#////                          ["TITLE", "URL", "TAGS"]]}


def Content():
    #    //             Suggest Branches for next steps
    #    //             If liked: Matplotlib, link to data analysis or Pandas maybe
    #    //             If liked: GUI stuff: Kivy, PyGame, Tkinter
    #    //             if liked: Text and word-based: NLTK

    # MAIN : [TITLE, URL, BODY_TEXT (LIST), HINTS(LIST)]
    TOPIC_DICT = {"Experiences": [["Add New", "admin.experience"],
                                  ["Manage", "admin.experience"],
                                 ],
                  "Images": [
                              ["Add New", "admin.images"],
                              ["Manage", "admin.images"],
                            ],
                  "Advert": [
                              ["Add New", "admin.advert"],
                              ["Manage", "admin.advert"],
                            ],
                  "Cart": [
                            ["Add New", "admin.cart"],
                            ["Manage", "admin.cart"],
                          ],
                  "Date_available": [
                              ["Add New", "admin.date"],
                              ["Manage", "admin.date"],
                            ],
                  "Flyer": [
                              ["Add New", "admin.flyer"],
                              ["Manage", "admin.flyer"],
                            ],
                  "Shop": [
                              ["Add New", "admin.shop"],
                              ["Manage", "admin.shop"],
                            ],
                  "Slideshow": [
                              ["Add New", "admin.slideshow"],
                              ["Manage", "admin.slideshow"],
                            ],
                  "Story": [
                              ["Add New", "admin.story"],
                              ["Manage", "admin.story"],
                            ],

                  }

    return TOPIC_DICT
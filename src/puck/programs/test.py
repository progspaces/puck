import logging

from ..actor import Actor

logger = logging.getLogger(__name__)

def run(self: Actor):
    logger.info("test_run has been called sucessfully")
    first_message=self.recieve()
    assert first_message[0]=="drawing_queue"
    drawing_queue= first_message[1]
    associated_canvas_ids=[]
    spawned_actors=[]
    while True:
        message = self.recieve()
        logger.debug("test_run has been gotten {message}")
        match message:
            case ("kill"):
                self.end()
                break
            case ("new_shape",("type", type),("coordinates", coordinates)):
                drawing_queue.put(("action", ("new", ("type", type), ("sender", self), ("coordinates", coordinates))))
            case ("update_shape",("id", id), ("coordinates", coordinates)):
                if associated_canvas_ids:
                    drawing_queue.put(("action", ("update", ("id", associated_canvas_ids[0]), ("coordinates", coordinates))))
                else:
                    logger.error("We have no associated canvas ids yet so we cannot update.")
            case ("information", *info):
                match info[0]:
                    case ("add_ids", id_list):
                        associated_canvas_ids.append(id_list)
                    case _ as info:
                        print(info)
            case _ as undefined:
                print(f"Youv'e given me this message: {undefined} \n" \
                      "I do not know what to do with it as I do not have a match case....")
    logger.info("test_run finished")

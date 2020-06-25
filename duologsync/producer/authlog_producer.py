import functools

from duologsync.producer.producer import Producer

class AuthlogProducer(Producer):
    """
    Implement the functionality of the Producer class to support the polling
    and placement into a queue of Authentication logs
    """

    def __init__(self, config, last_offset_read, log_queue, inherited_self):
        super().__init__(config, last_offset_read, log_queue, inherited_self)

        self.log_type = 'auth'

    async def _call_log_api(self, mintime):
        """
        Make a call to the authentication log endpoint and return the result
        of that API call

        @param mintime  The oldest timestamp acceptable for a new
                        administrator log

        @return the result of a call to the authentication log API endpoint
        """

        next_offset = self.last_offset_read.get('auth_last_fetched', None)
        return await self.loop.run_in_executor(
            self._executor,
            functools.partial(
                self.admin_api.get_authentication_log,
                api_version=2,
                mintime=mintime,
                next_offset=next_offset,
                sort='ts:asc',
                limit='1000'
            )
        )

    @staticmethod
    def _get_logs(api_result):
        """
        Retrieve authentication logs from the API result of a call to the
        authentication log endpoint

        @param api_result   The result of an API call to the authentication
                            log endpoint

        @return authentication logs from the result of an API call to the
                authentication log endpoint
        """

        return api_result['authlogs']

    @staticmethod
    def _get_last_offset_read(api_result):
        """
        Return the next_offset given by the result of a call to the
        authentication log API endpoint

        @param api_result   The result of an API call to the authentication
                            log endpoint

        @return the next_offset given by the result of a call to the
                authentication log API endpoint
        """

        return api_result['metadata']['next_offset']
